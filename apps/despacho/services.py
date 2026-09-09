"""Reglas de negocio de despacho (picking).

El picking nunca descuenta la existencia a mano: siempre pasa por
apps/inventario/services.registrar_salida(), que ya valida stock
insuficiente y bloquea la operación si no alcanza.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.despacho.models import Pedido
from apps.inventario import services as inventario_services


@transaction.atomic
def registrar_picking_linea(*, linea, cantidad, ubicacion_origen, usuario):
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser mayor a cero.")

    pendiente = linea.cantidad_solicitada - linea.cantidad_despachada
    if cantidad > pendiente:
        raise ValidationError(
            f"No puede despachar más de lo solicitado: pendiente {pendiente}, ingresado {cantidad}."
        )

    # registrar_salida ya lanza ValidationError si no hay stock suficiente.
    inventario_services.registrar_salida(
        producto=linea.producto,
        ubicacion=ubicacion_origen,
        cantidad=cantidad,
        usuario=usuario,
        documento_referencia=linea.pedido.numero,
    )

    linea.cantidad_despachada += cantidad
    linea.save(update_fields=["cantidad_despachada"])

    pedido = linea.pedido
    lineas = list(pedido.lineas.all())
    if all(l.cantidad_despachada >= l.cantidad_solicitada for l in lineas):
        pedido.estado = Pedido.Estado.DESPACHADO
    else:
        pedido.estado = Pedido.Estado.EN_PICKING
    pedido.save(update_fields=["estado"])

    return linea
