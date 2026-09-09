from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView

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
