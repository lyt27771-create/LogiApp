from django.contrib import admin

from apps.almacen.models import Bodega, Ubicacion, Zona


@admin.register(Bodega)
class BodegaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "direccion", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ("bodega", "codigo", "nombre", "tipo", "activo")
    list_filter = ("bodega", "tipo", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ("codigo", "zona", "capacidad_kg", "capacidad_m3", "activo")
    list_filter = ("zona__bodega", "zona", "activo")
    search_fields = ("codigo", "pasillo", "rack", "nivel", "posicion")
