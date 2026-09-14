from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, View

from apps.almacen.models import Ubicacion
from apps.catalogo.models import Producto
from apps.inventario import services
from apps.inventario.models import Movimiento


class MovimientoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """El kardex: listado de solo lectura, nunca se edita ni se borra desde pantalla."""

    model = Movimiento
    template_name = "inventario/listado.html"
    context_object_name = "movimientos"
    paginate_by = 15
    permission_required = "inventario.view_movimiento"

    def get_queryset(self):
        qs = Movimiento.objects.select_related(
            "producto", "ubicacion_origen", "ubicacion_destino", "usuario"
        ).order_by("-creado_en")
        tipo = self.request.GET.get("tipo", "").strip()
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tipos"] = Movimiento.TipoMovimiento.choices
        context["tipo_actual"] = self.request.GET.get("tipo", "")
        return context


class TrasladoCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Registrar un traslado entre ubicaciones. Nunca toca Existencia a mano:
    llama a inventario/services.py::registrar_traslado(), la única puerta
    de entrada al kardex para este tipo de movimiento."""

    template_name = "inventario/trasladar.html"
    permission_required = "inventario.add_movimiento"

    def _contexto(self):
        return {
            "productos": Producto.objects.filter(activo=True).order_by("sku"),
            "ubicaciones": Ubicacion.objects.filter(activo=True).order_by("codigo"),
        }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self._contexto())

    def post(self, request, *args, **kwargs):
        producto = get_object_or_404(Producto, pk=request.POST.get("producto"))
        ubicacion_origen = get_object_or_404(Ubicacion, pk=request.POST.get("ubicacion_origen"))
        ubicacion_destino = get_object_or_404(Ubicacion, pk=request.POST.get("ubicacion_destino"))

        try:
            cantidad = Decimal(request.POST.get("cantidad", ""))
            services.registrar_traslado(
                producto=producto,
                ubicacion_origen=ubicacion_origen,
                ubicacion_destino=ubicacion_destino,
                cantidad=cantidad,
                usuario=request.user,
                documento_referencia=request.POST.get("documento_referencia", ""),
            )
        except (InvalidOperation, TypeError):
            messages.error(request, "Ingresa una cantidad numérica válida.")
        except ValidationError as exc:
            messages.error(request, " ".join(exc.messages))
        else:
            messages.success(
                request,
                f"Traslado registrado: {cantidad} de {producto.sku} de "
                f"{ubicacion_origen.codigo} a {ubicacion_destino.codigo}.",
            )
            return redirect("inventario:listado")

        return redirect("inventario:trasladar")
