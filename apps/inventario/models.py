from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.almacen.models import Ubicacion
from apps.catalogo.models import Producto
from apps.core.models import ModeloBase


class Lote(ModeloBase):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="lotes")
    numero_lote = models.CharField(max_length=50)
    fecha_fabricacion = models.DateField(null=True, blank=True)
    fecha_caducidad = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        ordering = ["fecha_caducidad"]
        constraints = [
            models.UniqueConstraint(fields=["producto", "numero_lote"], name="unico_lote_por_producto"),
        ]

    def __str__(self):
        return f"{self.producto.sku} · Lote {self.numero_lote}"


class Existencia(models.Model):
    """El saldo actual. Se actualiza; nunca guarda historial (para eso está Movimiento)."""

    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="existencias")
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name="existencias")
    lote = models.ForeignKey(
        Lote, on_delete=models.PROTECT, related_name="existencias", null=True, blank=True
    )
    cantidad = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    cantidad_reservada = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Existencia"
        verbose_name_plural = "Existencias"
        constraints = [
            models.UniqueConstraint(
                fields=["producto", "ubicacion", "lote"], name="unica_existencia_producto_ubicacion_lote"
            ),
        ]

    @property
    def cantidad_disponible(self):
        return self.cantidad - self.cantidad_reservada

    def __str__(self):
        return f"{self.producto.sku} en {self.ubicacion.codigo}: {self.cantidad}"


class Movimiento(models.Model):
    """El kardex. Nunca se modifica ni se borra: es el historial auditable del almacén."""

    class TipoMovimiento(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"
        TRASLADO = "TRASLADO", "Traslado"
        AJUSTE_POSITIVO = "AJUSTE_POS", "Ajuste positivo"
        AJUSTE_NEGATIVO = "AJUSTE_NEG", "Ajuste negativo"
        DEVOLUCION = "DEVOLUCION", "Devolución"

    tipo = models.CharField(max_length=12, choices=TipoMovimiento.choices)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="movimientos")
    lote = models.ForeignKey(
        Lote, on_delete=models.PROTECT, related_name="movimientos", null=True, blank=True
    )
    ubicacion_origen = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name="movimientos_salida",
        null=True,
        blank=True,
    )
    ubicacion_destino = models.ForeignKey(
        Ubicacion,
        on_delete=models.PROTECT,
        related_name="movimientos_entrada",
        null=True,
        blank=True,
    )
    cantidad = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    documento_referencia = models.CharField(max_length=50, blank=True)
    observacion = models.TextField(blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="movimientos"
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Movimiento"
        verbose_name_plural = "Movimientos (Kardex)"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.creado_en:%Y-%m-%d %H:%M} · {self.tipo} · {self.producto.sku} · {self.cantidad}"
