from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """El sistema tiene únicamente dos tipos de usuario:

    - Administrador: se crea con createsuperuser, acceso total (incluye /admin/).
    - Operario: lo crea un Administrador desde Gestión de Usuarios, acceso solo
      a los módulos operativos (inventario, recepción, despacho), sin /admin/.
    """

    class Roles(models.TextChoices):
        ADMINISTRADOR = "ADMIN", "Administrador"
        OPERARIO = "OPERARIO", "Operario"

    cedula = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    rol = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.OPERARIO,
    )

    @property
    def es_administrador(self):
        return self.is_superuser

    def __str__(self):
        return self.username