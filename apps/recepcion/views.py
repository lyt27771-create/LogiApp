from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView

from apps.almacen.models import Ubicacion
from apps.recepcion import services
from apps.recepcion.models import LineaRecepcion, OrdenRecepcion


class OrdenRecepcionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = OrdenRecepcion
    template_name = "recepcion/listado.html"
    context_object_name = "ordenes"
    paginate_by = 10
    permission_required = "recepcion.view_ordenrecepcion"

    def get_queryset(self):
        qs = OrdenRecepcion.objects.select_related("proveedor").order_by("-fecha_esperada")
        estado = self.request.GET.get("estado", "").strip()
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["estados"] = OrdenRecepcion.Estado.choices
        context["estado_actual"] = self.request.GET.get("estado", "")
        return context


class OrdenRecepcionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = OrdenRecepcion
    template_name = "recepcion/detalle.html"
    context_object_name = "orden"
    permission_required = "recepcion.view_ordenrecepcion"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ubicaciones"] = Ubicacion.objects.filter(activo=True).order_by("codigo")
        lineas = list(self.object.lineas.select_related("producto").all())
        for linea in lineas:
            linea.pendiente = linea.cantidad_esperada - linea.cantidad_recibida
        context["lineas"] = lineas
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        linea = get_object_or_404(LineaRecepcion, pk=request.POST.get("linea_id"), orden=self.object)
        ubicacion = get_object_or_404(Ubicacion, pk=request.POST.get("ubicacion_destino"))

        try:
            cantidad = Decimal(request.POST.get("cantidad", ""))
            services.registrar_recepcion_linea(
                linea=linea, cantidad=cantidad, ubicacion_destino=ubicacion, usuario=request.user,
            )
        except (InvalidOperation, TypeError):
            messages.error(request, "Ingresa una cantidad numérica válida.")
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        else:
            messages.success(request, f"Recepción registrada: {cantidad} de {linea.producto.sku}.")

        return redirect("recepcion:detalle", pk=self.object.pk)
