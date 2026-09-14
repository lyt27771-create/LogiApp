from django.db import models

from apps.core.models import ModeloBase


class Bodega(ModeloBase):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "Bodega"
        verbose_name_plural = "Bodegas"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Zona(ModeloBase):
    class TipoZona(models.TextChoices):
        RECEPCION = "RECEPCION", "Recepción"
        ALMACENAJE = "ALMACENAJE", "Almacenaje"
        PICKING = "PICKING", "Picking"
        DESPACHO = "DESPACHO", "Despacho"
        CUARENTENA = "CUARENTENA", "Cuarentena"

    bodega = models.ForeignKey(Bodega, on_delete=models.PROTECT, related_name="zonas")
    codigo = models.CharField(max_length=10)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=15, choices=TipoZona.choices)

    class Meta:
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
        ordering = ["bodega", "codigo"]
        constraints = [
            models.UniqueConstraint(fields=["bodega", "codigo"], name="unico_codigo_zona_por_bodega"),
        ]

    def __str__(self):
        return f"{self.bodega.codigo} / {self.codigo} - {self.nombre}"


class Ubicacion(ModeloBase):
    zona = models.ForeignKey(Zona, on_delete=models.PROTECT, related_name="ubicaciones")
    pasillo = models.CharField(max_length=10)
    rack = models.CharField(max_length=10)
    nivel = models.CharField(max_length=10)
    posicion = models.CharField(max_length=10)
    codigo = models.CharField(max_length=60, unique=True, editable=False, blank=True)
    capacidad_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    capacidad_m3 = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    class Meta:
        verbose_name = "Ubicación"
        verbose_name_plural = "Ubicaciones"
        ordering = ["zona", "pasillo", "rack", "nivel", "posicion"]
        constraints = [
            models.UniqueConstraint(
                fields=["zona", "pasillo", "rack", "nivel", "posicion"],
                name="unica_ubicacion_fisica",
            ),
        ]

    def save(self, *args, **kwargs):
        self.codigo = (
            f"{self.zona.bodega.codigo}-{self.zona.codigo}-"
            f"{self.pasillo}-{self.rack}-{self.nivel}-{self.posicion}"
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo
