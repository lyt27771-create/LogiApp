from django.contrib import admin

from apps.recepcion.models import LineaRecepcion, OrdenRecepcion


class LineaRecepcionInline(admin.TabularInline):
    model = LineaRecepcion
    extra = 1


@admin.register(OrdenRecepcion)
class OrdenRecepcionAdmin(admin.ModelAdmin):
    list_display = ("numero", "proveedor", "fecha_esperada", "estado", "activo")
    list_filter = ("estado", "proveedor")
    search_fields = ("numero", "proveedor__razon_social")
    inlines = [LineaRecepcionInline]
