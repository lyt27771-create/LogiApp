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

Catálogo es **configuración de datos maestros**: por el diseño definitivo de roles, es exclusivo
del **Administrador** (superusuario). El grupo `Operario` no tiene `catalogo.view_producto` ni
ningún otro permiso sobre este módulo, así que un Operario ni ve el ícono en el sidebar ni puede
entrar a `/catalogo/` (403) ni a `/admin/catalogo/...` (bloqueado porque además no tiene
`is_staff`).

## Cómo probarlo

**Como administrador** (`admin` / `AdminWMS2026!`):
1. Entra a `http://127.0.0.1:8000/catalogo/` — debe verse el listado con los 10 productos de
   ejemplo, búsqueda por SKU/nombre y filtro por categoría.
2. Entra a `/admin/catalogo/producto/` — crea, edita y busca un producto. Confirma que el buscador
   (SKU o nombre) y el filtro por categoría funcionan.

**Como operario** (crea uno desde `/usuarios/crear/`, o usa `operario1` / `Operario2026!`):
1. Inicia sesión: cae en el "Dashboard Operativo" y el sidebar **no** muestra el ícono de Catálogo.
2. `/catalogo/` responde **403**; `/admin/catalogo/producto/` redirige al login del admin (no tiene
   `is_staff`, así que ni con sus credenciales correctas puede entrar ahí).

**Sin sesión:** cualquiera de las URLs de arriba redirige a `/accounts/login/`.

Ver también `docs/usuarios/README.md` para el módulo de Gestión de Usuarios y el detalle completo
de los dos roles del sistema.
