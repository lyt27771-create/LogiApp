from django.contrib import admin

from apps.despacho.models import Cliente, LineaPedido, Pedido


class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 1


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("razon_social", "identificacion", "telefono", "activo")
    search_fields = ("razon_social", "identificacion")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("numero", "cliente", "fecha_solicitud", "estado", "prioridad")
    list_filter = ("estado", "prioridad")
    search_fields = ("numero", "cliente__razon_social")
    inlines = [LineaPedidoInline]
