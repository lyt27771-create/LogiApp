from django.urls import path

from apps.usuarios.views import UsuarioCreateView, UsuarioListView, UsuarioUpdateView

app_name = "usuarios"

urlpatterns = [
    path("", UsuarioListView.as_view(), name="listado"),
    path("crear/", UsuarioCreateView.as_view(), name="crear"),
    path("<int:pk>/editar/", UsuarioUpdateView.as_view(), name="editar"),
]
