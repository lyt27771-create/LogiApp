"""Reglas de negocio de recepción.

Registrar lo recibido nunca actualiza la existencia a mano: siempre pasa
por apps/inventario/services.registrar_entrada(), que es la única puerta
de entrada al kardex.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventario import services as inventario_services
from apps.recepcion.models import OrdenRecepcion


@transaction.atomic
def registrar_recepcion_linea(*, linea, cantidad, ubicacion_destino, usuario):
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser mayor a cero.")

    pendiente = linea.cantidad_esperada - linea.cantidad_recibida
    if cantidad > pendiente:
        raise ValidationError(
            f"No puede recibir más de lo pendiente: pendiente {pendiente}, ingresado {cantidad}."
        )

    inventario_services.registrar_entrada(
        producto=linea.producto,
        ubicacion=ubicacion_destino,
        cantidad=cantidad,
        usuario=usuario,
        documento_referencia=linea.orden.numero,
    )

    linea.cantidad_recibida += cantidad
    linea.save(update_fields=["cantidad_recibida"])

    orden = linea.orden
    lineas = list(orden.lineas.all())
    if all(l.cantidad_recibida >= l.cantidad_esperada for l in lineas):
        orden.estado = OrdenRecepcion.Estado.COMPLETADA
    elif any(l.cantidad_recibida > 0 for l in lineas):
        orden.estado = OrdenRecepcion.Estado.PARCIAL
    orden.save(update_fields=["estado"])

    return linea
