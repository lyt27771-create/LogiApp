from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.views.generic import ListView

from apps.catalogo.models import Categoria, Producto


class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = "catalogo/listado.html"
    context_object_name = "productos"
    paginate_by = 10
    permission_required = "catalogo.view_producto"

    def get_queryset(self):
        qs = (
            Producto.objects.select_related("categoria", "unidad_medida")
            .filter(activo=True)
            .order_by("sku")
        )
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(sku__icontains=q) | Q(nombre__icontains=q))
        categoria_id = self.request.GET.get("categoria", "").strip()
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorias"] = Categoria.objects.filter(activo=True).order_by("nombre")
        context["q"] = self.request.GET.get("q", "")
        context["categoria_id"] = self.request.GET.get("categoria", "")
        return context
