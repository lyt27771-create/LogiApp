from django.urls import path

from apps.recepcion.views import OrdenRecepcionDetailView, OrdenRecepcionListView

app_name = "recepcion"

urlpatterns = [
    path("", OrdenRecepcionListView.as_view(), name="listado"),
    path("<int:pk>/", OrdenRecepcionDetailView.as_view(), name="detalle"),
]
