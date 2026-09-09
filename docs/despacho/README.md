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

Listado y detalle (y la acción de "Despachar"/picking) exigen `despacho.view_pedido`. Despacho es
uno de los tres módulos operativos: el grupo único **Operario** tiene ese permiso, y
`cargar_datos_demo` deja listo `operario1` / `Operario2026!` — así es como un Operario "registra
salidas de inventario" sin acceso a Catálogo ni a Almacén.

## Cómo probarlo

**Como administrador** (`admin` / `AdminWMS2026!`) o **como operario** (`operario1` /
`Operario2026!` — el flujo es idéntico para ambos):
1. `http://127.0.0.1:8000/despacho/` — deben verse los 2 pedidos de ejemplo (3 líneas cada uno).
2. Entra al detalle de un pedido con líneas pendientes, ingresa una cantidad y una ubicación de
   origen, y pulsa "Despachar": debe actualizar "Despachado", recalcular el estado del pedido
   (en picking/despachado) y **crear un movimiento de SALIDA** visible en `/inventario/`.
3. Prueba de stock insuficiente: pide despachar más de lo que hay disponible en esa ubicación
   (pero dentro de lo "pendiente" del pedido) — debe rechazarse con el mensaje de
   `registrar_salida` ("Stock insuficiente..."), sin descontar nada.

Como operario, además confirma que no hay forma de eliminar un pedido ni una línea desde esta
pantalla, y que `/catalogo/`, `/almacen/` y `/usuarios/` quedan fuera de alcance.

**Sin sesión:** redirige al login.
