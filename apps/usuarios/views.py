from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import CreateView, ListView, UpdateView

from apps.usuarios.forms import UsuarioCreationForm, UsuarioEditForm
from apps.usuarios.models import Usuario


class SoloAdministradorMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Gestión de Usuarios es exclusiva del Administrador (is_superuser).

    A diferencia de los demás módulos, aquí no se usa un permiso Django
    normal: el sistema define "Administrador" como quien se crea con
    createsuperuser, y esa condición no se puede otorgar por permiso.
    """

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Solo el administrador puede gestionar usuarios.")
        return redirect("dashboard")


class UsuarioListView(SoloAdministradorMixin, ListView):
    model = Usuario
    template_name = "usuarios/listado.html"
    context_object_name = "usuarios"
    paginate_by = 15

    def get_queryset(self):
        qs = Usuario.objects.order_by("username")
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(username__icontains=q) | qs.filter(first_name__icontains=q) | qs.filter(last_name__icontains=q)
        rol = self.request.GET.get("rol", "").strip()
        if rol:
            qs = qs.filter(rol=rol)
        estado = self.request.GET.get("estado", "").strip()
        if estado == "activo":
            qs = qs.filter(is_active=True)
        elif estado == "inactivo":
            qs = qs.filter(is_active=False)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["roles"] = Usuario.Roles.choices
        context["q"] = self.request.GET.get("q", "")
        context["rol_actual"] = self.request.GET.get("rol", "")
        context["estado_actual"] = self.request.GET.get("estado", "")
        return context

    def post(self, request, *args, **kwargs):
        """Acciones rápidas desde la fila de la tabla: activar/desactivar y
        restablecer contraseña."""
        usuario = get_object_or_404(Usuario, pk=request.POST.get("usuario_id"))
        accion = request.POST.get("accion")

        if usuario.is_superuser:
            messages.error(request, "No se puede modificar a otro administrador desde aquí.")
            return redirect("usuarios:listado")

        if accion == "toggle_activo":
            usuario.is_active = not usuario.is_active
            usuario.save(update_fields=["is_active"])
            estado = "activado" if usuario.is_active else "desactivado"
            messages.success(request, f"Usuario {usuario.username} {estado}.")
        elif accion == "restablecer_password":
            nueva_clave = get_random_string(10)
            usuario.set_password(nueva_clave)
            usuario.save(update_fields=["password"])
            messages.success(
                request,
                f"Contraseña de {usuario.username} restablecida. Nueva contraseña temporal: {nueva_clave}",
            )

        return redirect("usuarios:listado")


class UsuarioCreateView(SoloAdministradorMixin, CreateView):
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = "usuarios/form.html"
    success_url = reverse_lazy("usuarios:listado")

    def form_valid(self, form):
        usuario = form.save(commit=False)
        # Por definicion del sistema: todo usuario creado desde aqui es
        # Operario, activo, sin permisos administrativos.
        usuario.rol = Usuario.Roles.OPERARIO
        usuario.is_staff = False
        usuario.is_superuser = False
        usuario.is_active = True
        usuario.save()
        grupo, _ = Group.objects.get_or_create(name="Operario")
        usuario.groups.add(grupo)
        messages.success(self.request, f"Usuario {usuario.username} creado como Operario.")
        return redirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Crear usuario"
        return context


class UsuarioUpdateView(SoloAdministradorMixin, UpdateView):
    model = Usuario
    form_class = UsuarioEditForm
    template_name = "usuarios/form.html"
    success_url = reverse_lazy("usuarios:listado")

    def get_queryset(self):
        # Un administrador no edita a otro administrador desde esta pantalla.
        return Usuario.objects.filter(is_superuser=False)

    def form_valid(self, form):
        messages.success(self.request, f"Usuario {self.object.username} actualizado.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f"Editar usuario · {self.object.username}"
        return context
