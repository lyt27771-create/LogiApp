# Módulo Catálogo

## Qué hace

Maestro de productos del WMS: `Categoria` (jerárquica), `UnidadMedida`, `Proveedor` y `Producto`
(SKU único, código de barras, clasificación ABC, stock mínimo/máximo, si controla lote o
caducidad). Vive en `apps/catalogo/`.

| Archivo | Responsabilidad |
|---|---|
| `apps/catalogo/models.py` | `Categoria`, `UnidadMedida`, `Proveedor`, `Producto` |
| `apps/catalogo/admin.py` | Buscador por SKU/nombre, filtro por categoría y ABC |
| `apps/catalogo/views.py` | `ProductoListView`: listado en pantalla con búsqueda, filtro y paginación |
| `apps/catalogo/urls.py` | `catalogo:listado` → `/catalogo/` |
| `templates/catalogo/listado.html` | Plantilla del listado |

## Permisos

El listado (`ProductoListView`) y el admin exigen `catalogo.view_producto`. Un operario de este
módulo necesita además `catalogo.add_producto` para dar de alta productos.

`cargar_datos_demo` ya crea el grupo **Operario Catálogo** con esos dos permisos, y el usuario
`operario_catalogo` / `Operario2026!` (queda en ese grupo).

## Cómo probarlo

**Como administrador** (`admin`):
1. Entra a `http://127.0.0.1:8000/catalogo/` — debe verse el listado con los 10 productos de
   ejemplo, búsqueda por SKU/nombre y filtro por categoría.
2. Entra a `/admin/catalogo/producto/` — crea, edita y busca un producto. Confirma que el buscador
   (SKU o nombre) y el filtro por categoría funcionan.

**Como operario** (`operario_catalogo` / `Operario2026!`):
1. Inicia sesión. El tablero abre normal.
2. `/catalogo/` responde 200 (puede ver y, desde el admin, agregar productos).
3. Prueba entrar a `/almacen/`, `/inventario/`, `/recepcion/` o `/despacho/`: debe dar **403**
   (no puede entrar a módulos ajenos). Lo mismo entrando a `/admin/almacen/bodega/`, etc.
4. En `/admin/catalogo/producto/` no debe aparecer la opción de eliminar (no tiene
   `delete_producto`).

**Sin sesión:** cualquiera de las URLs de arriba redirige a `/accounts/login/`.
