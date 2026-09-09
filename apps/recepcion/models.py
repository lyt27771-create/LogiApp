from django.core.validators import MinValueValidator
from django.db import models

from apps.catalogo.models import Producto, Proveedor
from apps.core.models import ModeloBase


class OrdenRecepcion(ModeloBase):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        PARCIAL = "PARCIAL", "Recibida parcialmente"
        COMPLETADA = "COMPLETADA", "Completada"
        CANCELADA = "CANCELADA", "Cancelada"

    numero = models.CharField(max_length=30, unique=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="ordenes_recepcion")
    fecha_esperada = models.DateField()
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    observacion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Orden de recepción"
        verbose_name_plural = "Órdenes de recepción"
        ordering = ["-fecha_esperada"]

    def __str__(self):
        return f"OR-{self.numero} · {self.proveedor.razon_social}"


class LineaRecepcion(models.Model):
    orden = models.ForeignKey(OrdenRecepcion, on_delete=models.CASCADE, related_name="lineas")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="lineas_recepcion")
    cantidad_esperada = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    cantidad_recibida = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = "Línea de recepción"
        verbose_name_plural = "Líneas de recepción"
        constraints = [
            models.UniqueConstraint(fields=["orden", "producto"], name="unico_producto_por_orden_recepcion"),
        ]

    def __str__(self):
        return f"{self.orden.numero} · {self.producto.sku}"
