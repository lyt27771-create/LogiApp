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

El listado y el admin exigen `almacen.view_ubicacion`; un operario necesita además
`almacen.add_ubicacion`. `cargar_datos_demo` crea el grupo **Operario Almacén** con ambos y el
usuario `operario_almacen` / `Operario2026!`.

## Cómo probarlo

**Como administrador** (`admin`):
1. `http://127.0.0.1:8000/almacen/` — deben verse las 12 ubicaciones de ejemplo (1 bodega, 3
   zonas), con los filtros de bodega y zona funcionando.
2. `/admin/almacen/ubicacion/` — el filtro lateral por bodega/zona debe funcionar igual.

**Como operario** (`operario_almacen` / `Operario2026!`):
1. `/almacen/` responde 200; `/catalogo/`, `/inventario/`, `/recepcion/`, `/despacho/` responden
   403 (y lo mismo en sus rutas de `/admin/...`).
2. No tiene opción de eliminar ubicaciones en el admin.

**Sin sesión:** cualquier URL de arriba redirige al login.
