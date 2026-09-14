from django.urls import path

from apps.inventario.views import MovimientoListView, TrasladoCreateView

app_name = "inventario"

urlpatterns = [
    path("", MovimientoListView.as_view(), name="listado"),
    path("trasladar/", TrasladoCreateView.as_view(), name="trasladar"),
]
