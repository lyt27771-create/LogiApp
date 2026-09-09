from django.urls import path

from apps.inventario.views import MovimientoListView

app_name = "inventario"

urlpatterns = [
    path("", MovimientoListView.as_view(), name="listado"),
]
