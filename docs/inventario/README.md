# Módulo Inventario

## Qué hace

El corazón del WMS: `Existencia` (el saldo actual, único por producto+ubicación+lote) y
`Movimiento` (el kardex: entrada, salida, traslado, ajuste o devolución). El kardex **nunca se
edita ni se borra** — ni desde el admin ni desde la pantalla — porque es el historial auditable.

Toda entrada, salida o traslado pasa **exclusivamente** por `apps/inventario/services.py`
(`registrar_entrada`, `registrar_salida`, `registrar_traslado`), cada una dentro de una
transacción atómica. `registrar_salida` valida el stock disponible y lanza `ValidationError` si no
alcanza — así es como Recepción y Despacho (ver sus propios `services.py`) generan movimientos sin
tocar `Existencia` a mano.

| Archivo | Responsabilidad |
|---|---|
| `apps/inventario/models.py` | `Lote`, `Existencia`, `Movimiento` |
| `apps/inventario/services.py` | Única puerta de entrada al kardex |
| `apps/inventario/admin.py` | `Existencia` editable; `Movimiento` bloqueado a solo lectura |
| `apps/inventario/views.py` | `MovimientoListView`: el kardex en pantalla, filtrable por tipo |
| `apps/inventario/urls.py` | `inventario:listado` → `/inventario/` |

## Permisos

El listado y el admin exigen `inventario.view_movimiento` (y `view_existencia` para consultar
saldos). A propósito **no se concede `add_movimiento`** a nadie que no sea superusuario: el kardex
solo nace de `services.py`. Inventario es uno de los tres módulos operativos (junto con Recepción
y Despacho): el grupo único **Operario** tiene esos dos permisos de solo lectura, y
`cargar_datos_demo` deja listo el usuario `operario1` / `Operario2026!` para probarlo.

## Cómo probarlo

**Como administrador** (`admin` / `AdminWMS2026!`):
1. `http://127.0.0.1:8000/inventario/` — kardex completo, filtrable por tipo de movimiento.
2. `/admin/inventario/movimiento/` — confirma que **no** hay botón de agregar ni de editar/borrar
   un movimiento existente (solo "View").
3. Prueba de stock insuficiente: en el shell (`python manage.py shell`) o repitiendo lo que hace
   `cargar_datos_demo`, llama a `registrar_salida` con una cantidad mayor a la existencia — debe
   lanzar `ValidationError` con el mensaje "Stock insuficiente...".

**Como operario** (`operario1` / `Operario2026!`):
1. `/inventario/` responde 200 (de solo lectura, sin botón de agregar/editar); Catálogo y Almacén
   responden 403, y `/admin/` no es alcanzable.

**Sin sesión:** redirige al login.
