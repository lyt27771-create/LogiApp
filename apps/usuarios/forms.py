from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from apps.usuarios.models import Usuario


class LoginForm(AuthenticationForm):
    """AuthenticationForm de Django, solo con etiquetas y mensajes en español
    y las clases Bootstrap para el nuevo diseño del login."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": _(
            "Usuario o contraseña incorrectos. Verifica los datos e inténtalo de nuevo."
        ),
        "inactive": _("Esta cuenta está inactiva."),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuario o cédula"
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "1234567890", "autofocus": True}
        )
        self.fields["password"].label = "Contraseña"
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "••••••••"}
        )


class _CamposDarkMixin:
    """Aplica la clase CSS del tema oscuro a todos los campos del formulario."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " field-input").strip()


class UsuarioCreationForm(_CamposDarkMixin, UserCreationForm):
    """Formulario de 'Crear usuario' de Gestión de Usuarios.

    Siempre crea un Operario: el rol no es un campo del formulario porque,
    por definición del sistema, un Administrador solo se crea con
    createsuperuser. La vista que usa este formulario es la que agrega al
    usuario al grupo "Operario" y fija is_staff/is_superuser en False.
    """

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "first_name", "last_name", "cedula", "telefono", "email")
        labels = {
            "username": "Usuario o cédula",
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "cedula": "Cédula",
            "telefono": "Teléfono",
            "email": "Correo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Contraseña"
        self.fields["password1"].help_text = "Mínimo 8 caracteres; que no sea solo numérica ni demasiado común."
        self.fields["password2"].label = "Confirmar contraseña"
        self.fields["password2"].help_text = "Repite la misma contraseña para verificarla."


class UsuarioEditForm(_CamposDarkMixin, forms.ModelForm):
    """Edición de datos de un Operario: nunca cambia rol ni contraseña
    (la contraseña se restablece con una acción aparte)."""

    class Meta:
        model = Usuario
        fields = ("first_name", "last_name", "cedula", "telefono", "email")
        labels = {
            "first_name": "Nombres",
            "last_name": "Apellidos",
            "cedula": "Cédula",
            "telefono": "Teléfono",
            "email": "Correo",
        }
