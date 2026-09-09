from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView

from apps.almacen.models import Ubicacion
from apps.despacho import services
from apps.despacho.models import LineaPedido, Pedido


class PedidoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Pedido
    template_name = "despacho/listado.html"
    context_object_name = "pedidos"
    paginate_by = 10
    permission_required = "despacho.view_pedido"

    def get_queryset(self):
        qs = Pedido.objects.select_related("cliente").order_by("-fecha_solicitud")
        estado = self.request.GET.get("estado", "").strip()
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estados"] = Pedido.Estado.choices
        context["estado_actual"] = self.request.GET.get("estado", "")
        return context


class PedidoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Pedido
    template_name = "despacho/detalle.html"
    context_object_name = "pedido"
    permission_required = "despacho.view_pedido"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ubicaciones"] = Ubicacion.objects.filter(activo=True).order_by("codigo")
        lineas = list(self.object.lineas.select_related("producto").all())
        for linea in lineas:
            linea.pendiente = linea.cantidad_solicitada - linea.cantidad_despachada
        context["lineas"] = lineas
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        linea = get_object_or_404(LineaPedido, pk=request.POST.get("linea_id"), pedido=self.object)
        ubicacion = get_object_or_404(Ubicacion, pk=request.POST.get("ubicacion_origen"))

        try:
            cantidad = Decimal(request.POST.get("cantidad", ""))
            services.registrar_picking_linea(
                linea=linea, cantidad=cantidad, ubicacion_origen=ubicacion, usuario=request.user,
            )
        except (InvalidOperation, TypeError):
            messages.error(request, "Ingresa una cantidad numérica válida.")
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        else:
            messages.success(request, f"Picking registrado: {cantidad} de {linea.producto.sku}.")

        return redirect("despacho:detalle", pk=self.object.pk)
