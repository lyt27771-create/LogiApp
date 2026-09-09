from django.urls import path

from apps.despacho.views import PedidoDetailView, PedidoListView

app_name = "despacho"

urlpatterns = [
    path("", PedidoListView.as_view(), name="listado"),
    path("<int:pk>/", PedidoDetailView.as_view(), name="detalle"),
]
