# Módulo Usuarios (roles definitivos)

## Qué hace

El sistema tiene **únicamente dos tipos de usuario**:

- **Administrador**: se crea con `createsuperuser` (`is_superuser=True`). Acceso total: todos los
  módulos, `/admin/`, gestión de usuarios, reportes y configuración.
- **Operario**: lo crea un Administrador desde esta pantalla. `is_staff=False` siempre (por lo
  tanto **nunca** puede entrar a `/admin/`, Django lo bloquea solo), pertenece al grupo Django
  `Operario` y solo puede: consultar el catálogo indirectamente a través de sus tareas, registrar
  entradas/salidas (Recepción y Despacho) y consultar el Kardex (Inventario). No puede crear,
  editar ni eliminar usuarios, ni entrar a Catálogo o Almacén (son configuración, exclusiva del
  Administrador).

| Archivo | Responsabilidad |
|---|---|
| `apps/usuarios/models.py` | `Usuario` (extiende `AbstractUser`), `Roles.ADMINISTRADOR` / `Roles.OPERARIO` |
| `apps/usuarios/forms.py` | `UsuarioCreationForm` (crea siempre un Operario), `UsuarioEditForm` |
| `apps/usuarios/views.py` | `UsuarioListView` (+ acciones activar/desactivar/restablecer), `UsuarioCreateView`, `UsuarioUpdateView` |
| `apps/usuarios/urls.py` | `usuarios:listado` → `/usuarios/`, `usuarios:crear`, `usuarios:editar` |
| `templates/usuarios/` | `listado.html`, `form.html` |

## Permisos

Toda la sección está protegida por `SoloAdministradorMixin`, que exige `request.user.is_superuser`
— **no** un permiso Django normal, porque "Administrador" es por definición quien se creó con
`createsuperuser`, y esa condición no se puede delegar otorgando un permiso. Un Operario que
intenta entrar a `/usuarios/...` es redirigido al tablero con el mensaje "Solo el administrador
puede gestionar usuarios."; el ícono "Usuarios" del sidebar tampoco se muestra.

Al crear un usuario desde `/usuarios/crear/`: rol = Operario, `is_active=True`, `is_staff=False`,
`is_superuser=False`, y se lo agrega automáticamente al grupo `Operario` (los permisos operativos
de ese grupo se configuran una sola vez en `cargar_datos_demo`, sección `_crear_roles_operario`).

## Cómo probarlo

**Como administrador** (`admin` / `AdminWMS2026!`):
1. El sidebar muestra el ícono "Usuarios" (👤); el tablero dice "Dashboard Administrativo".
2. `/usuarios/` — listado, busca por usuario/nombre, filtra por rol y por estado.
3. "+ Crear usuario": llena el formulario (usuario, nombres, contraseña) y guarda. Confirma que
   queda como Operario, activo, y aparece en el listado.
4. "Editar" sobre ese usuario: cambia nombre/teléfono/correo y guarda.
5. "Desactivar": el estado cambia a Inactivo. Ese usuario ya no puede iniciar sesión (Django
   rechaza el login de un `is_active=False`).
6. "Restablecer contraseña": genera y muestra una contraseña temporal una sola vez, en un mensaje.
7. Ningún administrador (fila de `admin`) tiene acciones disponibles — no se gestiona a otro
   superusuario desde esta pantalla.

**Como operario** (`operario1` / `Operario2026!`):
1. El sidebar **no** muestra "Usuarios"; el tablero dice "Dashboard Operativo".
2. `/usuarios/` redirige al tablero con el mensaje de error; `/usuarios/crear/` igual.
3. `/admin/` no es alcanzable en absoluto (sin `is_staff`).

**Sin sesión:** cualquier URL de arriba redirige a `/accounts/login/`. Tras iniciar sesión, ambos
roles caen en la misma URL (`/`), pero el contenido que ven —y el sidebar— difiere según el rol:
Administrador ve el Dashboard Administrativo, Operario el Dashboard Operativo.
