# Módulo Despacho

## Qué hace

`Cliente`, `Pedido` (con estado y prioridad) y `LineaPedido` (cantidad solicitada vs. despachada).
El picking **no** descuenta la existencia a mano: `apps/despacho/services.py::registrar_picking_linea()`
valida que no se despache más de lo solicitado y llama a
`apps/inventario/services.py::registrar_salida()`, que ya valida el stock disponible y bloquea la
operación si no alcanza.

| Archivo | Responsabilidad |
|---|---|
| `apps/despacho/models.py` | `Cliente`, `Pedido`, `LineaPedido` |
| `apps/despacho/services.py` | `registrar_picking_linea()` |
| `apps/despacho/views.py` | `PedidoListView` + `PedidoDetailView` (con el form de picking) |
| `apps/despacho/urls.py` | `despacho:listado` → `/despacho/`, `despacho:detalle` → `/despacho/<id>/` |
| `templates/despacho/` | `listado.html`, `detalle.html` |

## Permisos

Listado y detalle exigen `despacho.view_pedido`; un operario necesita además
`despacho.add_pedido`. `cargar_datos_demo` crea el grupo **Operario Despacho** con ambos y el
usuario `operario_despacho` / `Operario2026!`.

## Cómo probarlo

**Como administrador** (`admin`):
1. `http://127.0.0.1:8000/despacho/` — deben verse los 2 pedidos de ejemplo (3 líneas cada uno).
2. Entra al detalle de un pedido con líneas pendientes, ingresa una cantidad y una ubicación de
   origen, y pulsa "Despachar": debe actualizar "Despachado", recalcular el estado del pedido
   (en picking/despachado) y **crear un movimiento de SALIDA** visible en `/inventario/`.
3. Prueba de stock insuficiente: pide despachar más de lo que hay disponible en esa ubicación
   (pero dentro de lo "pendiente" del pedido) — debe rechazarse con el mensaje de
   `registrar_salida` ("Stock insuficiente..."), sin descontar nada.

**Como operario** (`operario_despacho` / `Operario2026!`):
1. `/despacho/` responde 200; el resto de módulos responde 403.

**Sin sesión:** redirige al login.
