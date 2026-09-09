from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


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
