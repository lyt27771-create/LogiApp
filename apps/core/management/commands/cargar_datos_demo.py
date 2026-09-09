from decimal import Decimal

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.almacen.models import Bodega, Ubicacion, Zona
from apps.catalogo.models import Categoria, Producto, Proveedor, UnidadMedida
from apps.despacho.models import Cliente, LineaPedido, Pedido
from apps.inventario import services
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

        bodega, _ = Bodega.objects.get_or_create(
            codigo="B1", defaults={"nombre": "Bodega Central", "direccion": "Tulcán, Ecuador"}
        )
        zona_recepcion, _ = Zona.objects.get_or_create(
            bodega=bodega, codigo="REC", defaults={"nombre": "Recepción", "tipo": Zona.TipoZona.RECEPCION}
        )
        zona_almacenaje, _ = Zona.objects.get_or_create(
            bodega=bodega, codigo="ALM", defaults={"nombre": "Almacenaje", "tipo": Zona.TipoZona.ALMACENAJE}
        )
        ubicaciones = []
        for rack, nivel in [("A", "1"), ("A", "2"), ("B", "1"), ("B", "2")]:
            ubic, _ = Ubicacion.objects.get_or_create(
                zona=zona_almacenaje, pasillo="1", rack=rack, nivel=nivel, posicion="1",
                defaults={"capacidad_kg": 500, "capacidad_m3": 2},
            )
            ubicaciones.append(ubic)
        ubic_recepcion, _ = Ubicacion.objects.get_or_create(
            zona=zona_recepcion, pasillo="0", rack="0", nivel="0", posicion="0"
        )

        categorias = {}
        for nombre in ["Abarrotes", "Limpieza", "Electrónica"]:
            categorias[nombre], _ = Categoria.objects.get_or_create(nombre=nombre)

        unidad_caja, _ = UnidadMedida.objects.get_or_create(nombre="Caja", defaults={"abreviatura": "CJ"})
        unidad_unidad, _ = UnidadMedida.objects.get_or_create(nombre="Unidad", defaults={"abreviatura": "UN"})

        proveedor, _ = Proveedor.objects.get_or_create(
            ruc="1791234567001",
            defaults={"razon_social": "Distribuidora Andina S.A.", "telefono": "062960000"},
        )

        productos_datos = [
            ("SKU-0001", "Arroz 5kg", "Abarrotes", unidad_caja, "A", 20, 100, 4.50),
            ("SKU-0002", "Aceite vegetal 1L", "Abarrotes", unidad_caja, "A", 15, 80, 3.20),
            ("SKU-0003", "Detergente 1kg", "Limpieza", unidad_caja, "B", 10, 60, 2.80),
            ("SKU-0004", "Desinfectante 900ml", "Limpieza", unidad_unidad, "B", 8, 50, 3.90),
            ("SKU-0005", "Audífonos bluetooth", "Electrónica", unidad_unidad, "C", 5, 30, 18.00),
            ("SKU-0006", "Cable USB-C", "Electrónica", unidad_unidad, "C", 10, 40, 4.75),
        ]
        productos = []
        for sku, nombre, cat, unidad, abc, stock_min, stock_max, costo in productos_datos:
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

        # Entradas: llenan la mayoría de productos por encima del mínimo.
        cantidades_entrada = [80, 60, 5, 40, 25, 4]
        for producto, ubic, cantidad in zip(productos, ubicaciones * 2, cantidades_entrada):
            if not producto.existencias.exists():
                services.registrar_entrada(
                    producto=producto, ubicacion=ubic_recepcion, cantidad=Decimal(cantidad),
                    usuario=usuario, documento_referencia="OR-DEMO-0001",
                )
                services.registrar_traslado(
                    producto=producto, ubicacion_origen=ubic_recepcion, ubicacion_destino=ubic,
                    cantidad=Decimal(cantidad), usuario=usuario, documento_referencia="PUTAWAY-DEMO",
                )

        # Un par de salidas para que el kardex tenga variedad de tipos.
        if productos[0].existencias.filter(ubicacion=ubicaciones[0]).exists():
            services.registrar_salida(
                producto=productos[0], ubicacion=ubicaciones[0], cantidad=Decimal(10),
                usuario=usuario, documento_referencia="PED-DEMO-0001",
            )
        if productos[1].existencias.filter(ubicacion=ubicaciones[1]).exists():
            services.registrar_salida(
                producto=productos[1], ubicacion=ubicaciones[1], cantidad=Decimal(8),
                usuario=usuario, documento_referencia="PED-DEMO-0002",
            )

        cliente, _ = Cliente.objects.get_or_create(
            identificacion="0400000001", defaults={"razon_social": "Supermercado El Carchi"}
        )
        pedido, created = Pedido.objects.get_or_create(
            numero="PED-DEMO-0001",
            defaults={"cliente": cliente, "estado": Pedido.Estado.PENDIENTE, "prioridad": Pedido.Prioridad.ALTA},
        )
        if created:
            LineaPedido.objects.create(pedido=pedido, producto=productos[0], cantidad_solicitada=10)

        orden, created = OrdenRecepcion.objects.get_or_create(
            numero="OR-DEMO-0002",
            defaults={"proveedor": proveedor, "fecha_esperada": "2026-09-15", "estado": OrdenRecepcion.Estado.PENDIENTE},
        )
        if created:
            LineaRecepcion.objects.create(orden=orden, producto=productos[4], cantidad_esperada=30)

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
