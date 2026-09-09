from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import ModeloBase


class Categoria(ModeloBase):
    nombre = models.CharField(max_length=100, unique=True)
    categoria_padre = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subcategorias",
        verbose_name="Categoría padre",
    )

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class UnidadMedida(ModeloBase):
    nombre = models.CharField(max_length=50, unique=True)
    abreviatura = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = "Unidad de medida"
        verbose_name_plural = "Unidades de medida"
        ordering = ["nombre"]

    def __str__(self):
        return self.abreviatura


class Proveedor(ModeloBase):
    razon_social = models.CharField("Razón social", max_length=150)
    ruc = models.CharField("RUC", max_length=13, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ["razon_social"]

    def __str__(self):
        return self.razon_social


class Producto(ModeloBase):
    class ClasificacionABC(models.TextChoices):
        A = "A", "A - Alta rotación"
        B = "B", "B - Media rotación"
        C = "C", "C - Baja rotación"

    sku = models.CharField("SKU", max_length=30, unique=True)
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="productos")
    unidad_medida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, related_name="productos")
    proveedor_principal = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="productos",
        null=True,
        blank=True,
    )
    peso_kg = models.DecimalField(max_digits=10, decimal_places=3, default=0, validators=[MinValueValidator(0)])
    volumen_m3 = models.DecimalField(max_digits=10, decimal_places=4, default=0, validators=[MinValueValidator(0)])
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    stock_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    stock_maximo = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    clasificacion_abc = models.CharField(
        "Clasificación ABC", max_length=1, choices=ClasificacionABC.choices, default=ClasificacionABC.C
    )
    controla_lote = models.BooleanField(default=False)
    controla_caducidad = models.BooleanField(default=False)
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["sku"]

    def __str__(self):
        return f"{self.sku} - {self.nombre}"
