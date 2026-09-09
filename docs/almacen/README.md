# Módulo Almacén

## Qué hace

El layout físico del almacén: `Bodega`, `Zona` (recepción, almacenaje, picking, despacho o
cuarentena) y `Ubicacion` (pasillo-rack-nivel-posición, con capacidad en kg y m³ y un código único
que se genera solo, p. ej. `B1-ALM-1-A-1-1`). Vive en `apps/almacen/`.

| Archivo | Responsabilidad |
|---|---|
| `apps/almacen/models.py` | `Bodega`, `Zona`, `Ubicacion` |
| `apps/almacen/admin.py` | Filtro por bodega y por zona |
| `apps/almacen/views.py` | `UbicacionListView`: listado con filtro por bodega/zona y paginación |
| `apps/almacen/urls.py` | `almacen:listado` → `/almacen/` |
| `templates/almacen/listado.html` | Plantilla del listado |

## Permisos

Igual que Catálogo, Almacén es configuración del layout físico: exclusivo del **Administrador**.
El grupo `Operario` no tiene `almacen.view_ubicacion`, así que no ve el ícono en el sidebar y
`/almacen/` le da 403.

## Cómo probarlo

**Como administrador** (`admin` / `AdminWMS2026!`):
1. `http://127.0.0.1:8000/almacen/` — deben verse las 12 ubicaciones de ejemplo (1 bodega, 3
   zonas), con los filtros de bodega y zona funcionando.
2. `/admin/almacen/ubicacion/` — el filtro lateral por bodega/zona debe funcionar igual.

**Como operario** (`operario1` / `Operario2026!`, o cualquiera creado desde `/usuarios/crear/`):
1. El sidebar no muestra el ícono de Almacén.
2. `/almacen/` responde **403**; `/admin/almacen/...` no es alcanzable (sin `is_staff`).

**Sin sesión:** cualquier URL de arriba redirige al login.
