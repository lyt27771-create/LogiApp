from django.contrib import admin

from apps.catalogo.models import Categoria, Producto, Proveedor, UnidadMedida


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria_padre", "activo")
    list_filter = ("activo",)
    search_fields = ("nombre",)


@admin.register(UnidadMedida)
class UnidadMedidaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "abreviatura", "activo")
    search_fields = ("nombre", "abreviatura")


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "ruc", "telefono", "activo")
    list_filter = ("activo",)
    search_fields = ("razon_social", "ruc")


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "sku", "nombre", "categoria", "unidad_medida",
        "stock_minimo", "stock_maximo", "clasificacion_abc", "activo",
    )
    list_filter = ("categoria", "clasificacion_abc", "activo", "controla_lote", "controla_caducidad")
    search_fields = ("sku", "codigo_barras", "nombre")
