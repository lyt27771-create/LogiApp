from decimal import Decimal

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.almacen.models import Bodega, Ubicacion, Zona
from apps.catalogo.models import Categoria, Producto, Proveedor, UnidadMedida
from apps.despacho import services as despacho_services
from apps.despacho.models import Cliente, LineaPedido, Pedido
from apps.inventario import services as inventario_services
from apps.recepcion import services as recepcion_services
from apps.recepcion.models import LineaRecepcion, OrdenRecepcion
from apps.usuarios.models import Usuario

# Un grupo (y un usuario operario de ejemplo) por modulo, con permisos
# "solo de ver y agregar" tal como pide la rubrica de validacion por
# perfiles. Inventario es la excepcion: el kardex nunca se crea a mano,
# solo se puede ver.
ROLES_OPERARIO = {
    "Operario Catálogo": {
        "username": "operario_catalogo",
        "permisos": [("catalogo", "view_producto"), ("catalogo", "add_producto")],
    },
    "Operario Almacén": {
        "username": "operario_almacen",
        "permisos": [("almacen", "view_ubicacion"), ("almacen", "add_ubicacion")],
    },
    "Operario Inventario": {
        "username": "operario_inventario",
        "permisos": [("inventario", "view_movimiento"), ("inventario", "view_existencia")],
    },
    "Operario Recepción": {
        "username": "operario_recepcion",
        "permisos": [("recepcion", "view_ordenrecepcion"), ("recepcion", "add_ordenrecepcion")],
    },
    "Operario Despacho": {
        "username": "operario_despacho",
        "permisos": [("despacho", "view_pedido"), ("despacho", "add_pedido")],
    },
}
CONTRASENA_OPERARIOS_DEMO = "Operario2026!"


class Command(BaseCommand):
    help = "Carga bodega, ubicaciones, productos y movimientos de ejemplo para probar el sistema."

    @transaction.atomic
    def handle(self, *args, **options):
        usuario, _ = Usuario.objects.get_or_create(
            username="demo",
            defaults={"rol": Usuario.Roles.JEFE_BODEGA, "is_staff": True},
        )

        # --- Almacén: 1 bodega, 3 zonas, 12 ubicaciones ---
        bodega, _ = Bodega.objects.get_or_create(
            codigo="B1", defaults={"nombre": "Bodega Central", "direccion": "Tulcán, Ecuador"}
        )
        zona_recepcion, _ = Zona.objects.get_or_create(
            bodega=bodega, codigo="REC", defaults={"nombre": "Recepción", "tipo": Zona.TipoZona.RECEPCION}
        )
        zona_almacenaje, _ = Zona.objects.get_or_create(
            bodega=bodega, codigo="ALM", defaults={"nombre": "Almacenaje", "tipo": Zona.TipoZona.ALMACENAJE}
        )
        zona_despacho, _ = Zona.objects.get_or_create(
            bodega=bodega, codigo="DES", defaults={"nombre": "Despacho", "tipo": Zona.TipoZona.DESPACHO}
        )

        ubicaciones_almacenaje = []
        for rack in ("A", "B", "C", "D"):
            for nivel in ("1", "2"):
                ubic, _ = Ubicacion.objects.get_or_create(
                    zona=zona_almacenaje, pasillo="1", rack=rack, nivel=nivel, posicion="1",
                    defaults={"capacidad_kg": 500, "capacidad_m3": 2},
                )
                ubicaciones_almacenaje.append(ubic)  # 8 ubicaciones

        ubic_recepcion, _ = Ubicacion.objects.get_or_create(
            zona=zona_recepcion, pasillo="0", rack="0", nivel="0", posicion="0"
        )

        ubicaciones_despacho = []
        for posicion in ("1", "2", "3"):
            ubic, _ = Ubicacion.objects.get_or_create(
                zona=zona_despacho, pasillo="0", rack="0", nivel="0", posicion=posicion,
            )
            ubicaciones_despacho.append(ubic)  # 3 ubicaciones

        # Total: 8 + 1 + 3 = 12 ubicaciones.

        # --- Catálogo: 10 productos, 3 categorías, 2 proveedores ---
        categorias = {}
        for nombre in ["Abarrotes", "Limpieza", "Electrónica"]:
            categorias[nombre], _ = Categoria.objects.get_or_create(nombre=nombre)

        unidad_caja, _ = UnidadMedida.objects.get_or_create(nombre="Caja", defaults={"abreviatura": "CJ"})
        unidad_unidad, _ = UnidadMedida.objects.get_or_create(nombre="Unidad", defaults={"abreviatura": "UN"})

        proveedor_andina, _ = Proveedor.objects.get_or_create(
            ruc="1791234567001",
            defaults={"razon_social": "Distribuidora Andina S.A.", "telefono": "062960000"},
        )
        proveedor_norte, _ = Proveedor.objects.get_or_create(
            ruc="1791234568001",
            defaults={"razon_social": "Importadora Norte Cía. Ltda.", "telefono": "062961111"},
        )

        productos_datos = [
            ("SKU-0001", "Arroz 5kg", "Abarrotes", unidad_caja, "A", 20, 100, 4.50, proveedor_andina),
            ("SKU-0002", "Aceite vegetal 1L", "Abarrotes", unidad_caja, "A", 15, 80, 3.20, proveedor_andina),
            ("SKU-0003", "Detergente 1kg", "Limpieza", unidad_caja, "B", 10, 60, 2.80, proveedor_andina),
            ("SKU-0004", "Desinfectante 900ml", "Limpieza", unidad_unidad, "B", 8, 50, 3.90, proveedor_andina),
            ("SKU-0005", "Audífonos bluetooth", "Electrónica", unidad_unidad, "C", 5, 30, 18.00, proveedor_norte),
            ("SKU-0006", "Cable USB-C", "Electrónica", unidad_unidad, "C", 10, 40, 4.75, proveedor_norte),
            ("SKU-0007", "Azúcar 2kg", "Abarrotes", unidad_caja, "A", 20, 90, 2.50, proveedor_andina),
            ("SKU-0008", "Papel higiénico x4", "Limpieza", unidad_caja, "B", 10, 60, 3.10, proveedor_andina),
            ("SKU-0009", "Mouse inalámbrico", "Electrónica", unidad_unidad, "C", 5, 25, 9.90, proveedor_norte),
            ("SKU-0010", "Teclado USB", "Electrónica", unidad_unidad, "C", 5, 25, 12.50, proveedor_norte),
        ]
        productos = []
        for sku, nombre, cat, unidad, abc, stock_min, stock_max, costo, proveedor in productos_datos:
            prod, _ = Producto.objects.get_or_create(
                sku=sku,
                defaults={
                    "nombre": nombre,
                    "categoria": categorias[cat],
                    "unidad_medida": unidad,
                    "proveedor_principal": proveedor,
                    "clasificacion_abc": abc,
                    "stock_minimo": stock_min,
                    "stock_maximo": stock_max,
                    "costo_unitario": Decimal(str(costo)),
                },
            )
            productos.append(prod)

        # --- Inventario: entrada + traslado por producto, para tener saldo real ---
        cantidades_entrada = [80, 60, 5, 40, 25, 4, 70, 50, 15, 15]
        for i, (producto, cantidad) in enumerate(zip(productos, cantidades_entrada)):
            if not producto.existencias.exists():
                inventario_services.registrar_entrada(
                    producto=producto, ubicacion=ubic_recepcion, cantidad=Decimal(cantidad),
                    usuario=usuario, documento_referencia="OR-DEMO-0001",
                )
                destino = ubicaciones_almacenaje[i % len(ubicaciones_almacenaje)]
                inventario_services.registrar_traslado(
                    producto=producto, ubicacion_origen=ubic_recepcion, ubicacion_destino=destino,
                    cantidad=Decimal(cantidad), usuario=usuario, documento_referencia="PUTAWAY-DEMO",
                )

        # 1 salida "normal" (además de las que generen recepción/despacho más abajo).
        if not inventario_services.Movimiento.objects.filter(documento_referencia="AJUSTE-DEMO").exists():
            inventario_services.registrar_salida(
                producto=productos[1], ubicacion=ubicaciones_almacenaje[1], cantidad=Decimal(8),
                usuario=usuario, documento_referencia="AJUSTE-DEMO",
            )

        # 1 intento fallido: salida por encima del stock disponible (debe rechazarse).
        try:
            inventario_services.registrar_salida(
                producto=productos[0], ubicacion=ubicaciones_almacenaje[0], cantidad=Decimal(999999),
                usuario=usuario, documento_referencia="PRUEBA-STOCK-INSUFICIENTE",
            )
        except ValidationError as exc:
            self.stdout.write(self.style.WARNING(f"Intento fallido rechazado como se esperaba: {exc.messages[0]}"))

        # --- Despacho: 2 clientes, 2 pedidos con 3 líneas cada uno ---
        cliente_carchi, _ = Cliente.objects.get_or_create(
            identificacion="0400000001", defaults={"razon_social": "Supermercado El Carchi"}
        )
        cliente_tulcan, _ = Cliente.objects.get_or_create(
            identificacion="0400000002", defaults={"razon_social": "Comercial Tulcán"}
        )

        pedido1, _ = Pedido.objects.get_or_create(
            numero="PED-DEMO-0001",
            defaults={"cliente": cliente_carchi, "estado": Pedido.Estado.PENDIENTE, "prioridad": Pedido.Prioridad.ALTA},
        )
        for producto, cantidad in [(productos[0], 10), (productos[1], 6), (productos[2], 4)]:
            LineaPedido.objects.get_or_create(
                pedido=pedido1, producto=producto, defaults={"cantidad_solicitada": cantidad}
            )

        pedido2, _ = Pedido.objects.get_or_create(
            numero="PED-DEMO-0002",
            defaults={"cliente": cliente_tulcan, "estado": Pedido.Estado.PENDIENTE, "prioridad": Pedido.Prioridad.MEDIA},
        )
        for producto, cantidad in [(productos[6], 8), (productos[7], 5), (productos[8], 3)]:
            LineaPedido.objects.get_or_create(
                pedido=pedido2, producto=producto, defaults={"cantidad_solicitada": cantidad}
            )

        # Un picking real sobre el pedido 1, para demostrar el flujo completo.
        linea_pedido1 = pedido1.lineas.filter(producto=productos[0]).first()
        if linea_pedido1 and linea_pedido1.cantidad_despachada == 0:
            despacho_services.registrar_picking_linea(
                linea=linea_pedido1, cantidad=Decimal(5),
                ubicacion_origen=ubicaciones_almacenaje[0], usuario=usuario,
            )

        # --- Recepción: 2 órdenes con 3 líneas cada una ---
        orden1, _ = OrdenRecepcion.objects.get_or_create(
            numero="OR-DEMO-0001",
            defaults={"proveedor": proveedor_andina, "fecha_esperada": "2026-09-12", "estado": OrdenRecepcion.Estado.PENDIENTE},
        )
        for producto, cantidad in [(productos[0], 40), (productos[1], 30), (productos[2], 20)]:
            LineaRecepcion.objects.get_or_create(
                orden=orden1, producto=producto, defaults={"cantidad_esperada": cantidad}
            )

        orden2, _ = OrdenRecepcion.objects.get_or_create(
            numero="OR-DEMO-0002",
            defaults={"proveedor": proveedor_norte, "fecha_esperada": "2026-09-15", "estado": OrdenRecepcion.Estado.PENDIENTE},
        )
        for producto, cantidad in [(productos[4], 30), (productos[5], 20), (productos[8], 15)]:
            LineaRecepcion.objects.get_or_create(
                orden=orden2, producto=producto, defaults={"cantidad_esperada": cantidad}
            )

        # Una recepción real sobre la orden 2, para demostrar el flujo completo.
        linea_orden2 = orden2.lineas.filter(producto=productos[4]).first()
        if linea_orden2 and linea_orden2.cantidad_recibida == 0:
            recepcion_services.registrar_recepcion_linea(
                linea=linea_orden2, cantidad=Decimal(20),
                ubicacion_destino=ubic_recepcion, usuario=usuario,
            )

        self._crear_roles_operario()

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo cargados correctamente."))

    def _crear_roles_operario(self):
        for nombre_grupo, config in ROLES_OPERARIO.items():
            grupo, _ = Group.objects.get_or_create(name=nombre_grupo)
            permisos = [
                Permission.objects.get(content_type__app_label=app_label, codename=codename)
                for app_label, codename in config["permisos"]
            ]
            grupo.permissions.set(permisos)

            operario, creado = Usuario.objects.get_or_create(
                username=config["username"],
                defaults={"is_staff": True, "rol": Usuario.Roles.OPERARIO},
            )
            if creado:
                operario.set_password(CONTRASENA_OPERARIOS_DEMO)
                operario.is_staff = True
                operario.rol = Usuario.Roles.OPERARIO
                operario.save()
            operario.groups.add(grupo)

        self.stdout.write(
            self.style.SUCCESS(
                f"Usuarios operario de ejemplo listos (contraseña '{CONTRASENA_OPERARIOS_DEMO}'): "
                + ", ".join(cfg["username"] for cfg in ROLES_OPERARIO.values())
            )
        )
