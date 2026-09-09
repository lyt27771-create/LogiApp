from django.db import models


class ModeloBase(models.Model):
    """Campos comunes a los maestros del WMS: borrado lógico y auditoría de fechas."""

    activo = models.BooleanField(default=True, verbose_name="Activo")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
