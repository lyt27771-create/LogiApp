from django.contrib import admin

from apps.inventario.models import Existencia, Lote, Movimiento


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ("producto", "numero_lote", "fecha_fabricacion", "fecha_caducidad", "activo")
    list_filter = ("activo",)
    search_fields = ("producto__sku", "numero_lote")


@admin.register(Existencia)
class ExistenciaAdmin(admin.ModelAdmin):
    list_display = ("producto", "ubicacion", "lote", "cantidad", "cantidad_reservada", "cantidad_disponible")
    list_filter = ("ubicacion__zona__bodega",)
    search_fields = ("producto__sku", "ubicacion__codigo")


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    """El kardex es solo lectura: nunca se edita ni se borra un movimiento ya registrado."""

    list_display = (
        "creado_en", "tipo", "producto", "cantidad",
        "ubicacion_origen", "ubicacion_destino", "usuario",
    )
    list_filter = ("tipo", "creado_en")
    search_fields = ("producto__sku", "documento_referencia")
    date_hierarchy = "creado_en"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
