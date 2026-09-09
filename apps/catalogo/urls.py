from django.urls import path

from apps.catalogo.views import ProductoListView

app_name = "catalogo"

urlpatterns = [
    path("", ProductoListView.as_view(), name="listado"),
]
