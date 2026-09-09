"""Reglas de negocio del inventario.

Las vistas NUNCA modifican Existencia directamente: toda entrada, salida o
traslado pasa por una de estas funciones, que corre en una transacción
atómica. Así el inventario nunca queda descuadrado aunque falle a mitad del
proceso.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.inventario.models import Existencia, Movimiento


@transaction.atomic
def registrar_entrada(*, producto, ubicacion, cantidad, usuario, lote=None,
                       documento_referencia="", observacion=""):
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser mayor a cero.")

    existencia, _ = Existencia.objects.select_for_update().get_or_create(
        producto=producto, ubicacion=ubicacion, lote=lote,
        defaults={"cantidad": 0},
    )
    existencia.cantidad += cantidad
    existencia.save(update_fields=["cantidad", "actualizado_en"])

    return Movimiento.objects.create(
        tipo=Movimiento.TipoMovimiento.ENTRADA,
        producto=producto,
        lote=lote,
        ubicacion_destino=ubicacion,
        cantidad=cantidad,
        documento_referencia=documento_referencia,
        observacion=observacion,
        usuario=usuario,
    )


@transaction.atomic
def registrar_salida(*, producto, ubicacion, cantidad, usuario, lote=None,
                      documento_referencia="", observacion=""):
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser mayor a cero.")

    try:
        existencia = Existencia.objects.select_for_update().get(
            producto=producto, ubicacion=ubicacion, lote=lote,
        )
    except Existencia.DoesNotExist:
        raise ValidationError("No existe saldo de este producto en la ubicación indicada.")

    if existencia.cantidad_disponible < cantidad:
        raise ValidationError(
            f"Stock insuficiente: disponible {existencia.cantidad_disponible}, solicitado {cantidad}."
        )

    existencia.cantidad -= cantidad
    existencia.save(update_fields=["cantidad", "actualizado_en"])

    return Movimiento.objects.create(
        tipo=Movimiento.TipoMovimiento.SALIDA,
        producto=producto,
        lote=lote,
        ubicacion_origen=ubicacion,
        cantidad=cantidad,
        documento_referencia=documento_referencia,
        observacion=observacion,
        usuario=usuario,
    )


@transaction.atomic
def registrar_traslado(*, producto, ubicacion_origen, ubicacion_destino, cantidad, usuario,
                        lote=None, documento_referencia="", observacion=""):
    if cantidad <= 0:
        raise ValidationError("La cantidad debe ser mayor a cero.")
    if ubicacion_origen == ubicacion_destino:
        raise ValidationError("La ubicación de origen y destino no pueden ser la misma.")

    try:
        existencia_origen = Existencia.objects.select_for_update().get(
            producto=producto, ubicacion=ubicacion_origen, lote=lote,
        )
    except Existencia.DoesNotExist:
        raise ValidationError("No existe saldo de este producto en la ubicación de origen.")

    if existencia_origen.cantidad_disponible < cantidad:
        raise ValidationError(
            f"Stock insuficiente en origen: disponible {existencia_origen.cantidad_disponible}, "
            f"solicitado {cantidad}."
        )

    existencia_origen.cantidad -= cantidad
    existencia_origen.save(update_fields=["cantidad", "actualizado_en"])

    existencia_destino, _ = Existencia.objects.select_for_update().get_or_create(
        producto=producto, ubicacion=ubicacion_destino, lote=lote,
        defaults={"cantidad": 0},
    )
    existencia_destino.cantidad += cantidad
    existencia_destino.save(update_fields=["cantidad", "actualizado_en"])

    return Movimiento.objects.create(
        tipo=Movimiento.TipoMovimiento.TRASLADO,
        producto=producto,
        lote=lote,
        ubicacion_origen=ubicacion_origen,
        ubicacion_destino=ubicacion_destino,
        cantidad=cantidad,
        documento_referencia=documento_referencia,
        observacion=observacion,
        usuario=usuario,
    )
