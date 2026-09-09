from django.urls import path

from apps.almacen.views import UbicacionListView

app_name = "almacen"

urlpatterns = [
    path("", UbicacionListView.as_view(), name="listado"),
]
