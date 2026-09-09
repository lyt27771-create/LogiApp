from django.core.validators import MinValueValidator
from django.db import models

from apps.catalogo.models import Producto
from apps.core.models import ModeloBase


class Cliente(ModeloBase):
    razon_social = models.CharField("Razón social", max_length=150)
    identificacion = models.CharField(max_length=13, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social


class Pedido(ModeloBase):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        EN_PICKING = "PICKING", "En picking"
        LISTO = "LISTO", "Listo para despacho"
        DESPACHADO = "DESPACHADO", "Despachado"
        CANCELADO = "CANCELADO", "Cancelado"

    class Prioridad(models.TextChoices):
        ALTA = "ALTA", "Alta"
        MEDIA = "MEDIA", "Media"
        BAJA = "BAJA", "Baja"

    numero = models.CharField(max_length=30, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="pedidos")
    fecha_solicitud = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    prioridad = models.CharField(max_length=6, choices=Prioridad.choices, default=Prioridad.MEDIA)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-fecha_solicitud"]

    def __str__(self):
        return f"PED-{self.numero} · {self.cliente.razon_social}"


class LineaPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="lineas")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="lineas_pedido")
    cantidad_solicitada = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    cantidad_despachada = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )

    class Meta:
        verbose_name = "Línea de pedido"
        verbose_name_plural = "Líneas de pedido"
        constraints = [
            models.UniqueConstraint(fields=["pedido", "producto"], name="unico_producto_por_pedido"),
        ]

    def __str__(self):
        return f"{self.pedido.numero} · {self.producto.sku}"
