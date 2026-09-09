from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView

from apps.almacen.models import Bodega, Ubicacion, Zona


class UbicacionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Ubicacion
    template_name = "almacen/listado.html"
    context_object_name = "ubicaciones"
    paginate_by = 10
    permission_required = "almacen.view_ubicacion"

    def get_queryset(self):
        qs = (
            Ubicacion.objects.select_related("zona", "zona__bodega")
            .filter(activo=True)
            .order_by("zona__bodega", "zona", "pasillo", "rack", "nivel")
        )
        bodega_id = self.request.GET.get("bodega", "").strip()
        if bodega_id:
            qs = qs.filter(zona__bodega_id=bodega_id)
        zona_id = self.request.GET.get("zona", "").strip()
        if zona_id:
            qs = qs.filter(zona_id=zona_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["bodegas"] = Bodega.objects.filter(activo=True).order_by("codigo")
        context["zonas"] = Zona.objects.filter(activo=True).order_by("codigo")
        context["bodega_id"] = self.request.GET.get("bodega", "")
        context["zona_id"] = self.request.GET.get("zona", "")
        return context
