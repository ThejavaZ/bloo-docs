# Respuestas de error

> Estado: ✅ Implementado. Formatos reales que devuelve la API.

La API distingue tres familias de error: **validación** (422, formato nativo de Laravel), **negocio** (sobre `{success: false, message}`) e **infraestructura** (errores del framework). Todos los mensajes están en español.

## Catálogo por código

### 401 — No autenticado

Sin token, token revocado o sesión cerrada.

```json
{ "message": "Unauthenticated." }
```

> Es el único mensaje del sistema en inglés: viene del framework y el frontend lo trata de forma especial (limpia el token y redirige a `/login`).

### 403 — Sin permiso o alcance insuficiente

Incluye tres situaciones distintas, todas con el mismo formato:

| Situación | Mensaje típico |
|---|---|
| Acceso a un recurso de **otra empresa** | «No tienes permiso para realizar esta acción» |
| **Usuario inactivo** intentando operar | «Tu cuenta está deshabilitada» |
| Solicitud al Panel Landlord **sin rol superadmin** | «Se requiere rol Superadmin para acceder» |

```json
{
  "success": false,
  "message": "No tienes permiso para realizar esta acción"
}
```

### 404 — Recurso inexistente

Formato del framework:

```json
{ "message": "No query results for model [App\\Models\\Client] 9999" }
```

> El mensaje es interno y no está pensado para mostrarse tal cual al usuario final; el frontend lo traduce a un mensaje genérico.

### 409 — Conflicto de negocio

Situaciones que el servidor detecta como incompatibles con el estado actual. Ejemplo real: solicitar impersonar un tenant que no tiene usuarios elegibles.

```json
{
  "success": false,
  "message": "La empresa no tiene usuarios para impersonar"
}
```

### 422 — Validación

Formato nativo de Laravel, **sin** sobre `success`:

```json
{
  "message": "Los datos enviados no son válidos.",
  "errors": {
    "email": ["El campo email es obligatorio."],
    "name": ["El nombre debe tener al menos 3 caracteres."]
  }
}
```

El frontend muestra el primer mensaje del primer campo con error.

### 503 — Empresa en mantenimiento

El middleware de mantenimiento intercepta toda ruta de negocio de un tenant congelado:

```json
{
  "success": false,
  "maintenance": true,
  "message": "La empresa se encuentra en modo mantenimiento."
}
```

La bandera `maintenance: true` permite al cliente distinguir un mantenimiento programado de una caída del servicio. Quedan fuera del bloqueo las rutas `/api/auth/*` (logout, perfil, cambio de contraseña).

### 500 — Error inesperado

Formato estándar del framework. No se personaliza para no exponer detalles internos; el diagnóstico se hace en los logs (ver [../operations/logging.md](../operations/logging.md)).

## Tabla resumen

| Código | Formato | Origen | ¿Mostrar al usuario? |
|---|---|---|---|
| 401 | `{message}` | Framework | Sí («Sesión expirada») |
| 403 | `{success, message}` | Controller / middleware | Sí, tal cual |
| 404 | `{message}` | Framework | Mejor genérico |
| 409 | `{success, message}` | Controller | Sí, tal cual |
| 422 | `{message, errors}` | Validación | Sí, por campo |
| 503 | `{success, maintenance, message}` | Middleware | Sí, tal cual |
| 500 | Formato framework | Framework | No; genérico |

## Manejo en el cliente

El frontend normaliza todos los errores a `{status, message, …body}`:

- `status = 0` → sin respuesta (timeout o backend caído).
- 401 → toast «Sesión expirada» (deduplicado en ventana de 2.5 s), limpieza de token y redirect a `/login`.
- 403 → toast «Acceso denegado» y redirect a `/forbidden`.
- ≥ 500 → mensaje genérico en español; el detalle a consola y al Error Boundary.

El helper `getApiErrorMessage(error, fallback)` centraliza la traducción para las vistas.

## Recomendaciones

1. Un mensaje de error responde **qué pasó y qué hacer**; jamás expone trazas, SQL ni nombres de tablas.
2. Usa 403 (no 404) cuando el recurso existe pero pertenece a otro tenant: es más honesto y más fácil de monitorear.
3. `message` en singular, sin el código HTTP, sin mayúscula inicial arbitraria ni signo final.
4. Si agregas un código nuevo (por ejemplo, 423 o 429), documenta aquí su forma antes de emitirlo en producción.
