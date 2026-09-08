from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Roles(models.TextChoices):
        ADMINISTRADOR = "ADMIN", "Administrador"
        JEFE_BODEGA = "JEFE", "Jefe de Bodega"
        OPERARIO = "OPERARIO", "Operario"
        CONSULTA = "CONSULTA", "Consulta"

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
        default=Roles.CONSULTA,
    )

    def __str__(self):
        return self.username