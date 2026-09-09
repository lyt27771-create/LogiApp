# Módulo Recepción

## Qué hace

`OrdenRecepcion` (con estado: pendiente, parcial, completada, cancelada) y `LineaRecepcion`
(cantidad esperada vs. recibida por producto). Registrar lo recibido **no** actualiza la existencia
a mano: `apps/recepcion/services.py::registrar_recepcion_linea()` valida que no se reciba más de lo
pendiente, llama a `apps/inventario/services.py::registrar_entrada()` (la única puerta al kardex) y
recalcula el estado de la orden.

| Archivo | Responsabilidad |
|---|---|
| `apps/recepcion/models.py` | `OrdenRecepcion`, `LineaRecepcion` |
| `apps/recepcion/services.py` | `registrar_recepcion_linea()` |
| `apps/recepcion/views.py` | `OrdenRecepcionListView` + `OrdenRecepcionDetailView` (con el form de recepción) |
| `apps/recepcion/urls.py` | `recepcion:listado` → `/recepcion/`, `recepcion:detalle` → `/recepcion/<id>/` |
| `templates/recepcion/` | `listado.html`, `detalle.html` |

## Permisos

Listado y detalle exigen `recepcion.view_ordenrecepcion`; un operario necesita además
`recepcion.add_ordenrecepcion`. `cargar_datos_demo` crea el grupo **Operario Recepción** con ambos
y el usuario `operario_recepcion` / `Operario2026!`.

## Cómo probarlo

**Como administrador** (`admin`):
1. `http://127.0.0.1:8000/recepcion/` — deben verse las 2 órdenes de ejemplo (3 líneas cada una).
2. Entra al detalle de una orden con líneas pendientes, ingresa una cantidad y una ubicación de
   destino, y pulsa "Recibir": debe actualizar "Recibido", recalcular el estado de la orden
   (parcial/completada) y **crear un movimiento de ENTRADA** visible en `/inventario/`.
3. Intenta recibir más de lo pendiente: debe rechazarse con el mensaje "No puede recibir más de lo
   pendiente...", sin crear ningún movimiento.

**Como operario** (`operario_recepcion` / `Operario2026!`):
1. `/recepcion/` responde 200; el resto de módulos responde 403.

**Sin sesión:** redirige al login.
