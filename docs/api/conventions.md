# Convenciones de la API

> Estado: ✅ Implementado. Este documento define el **contrato general**; el listado exhaustivo de endpoints vive en [`erp-api/docs/API.md`](https://github.com/ThejavaZ/erp-api/blob/main/docs/API.md).

## Identidad del servicio

| Aspecto | Convención |
|---|---|
| Base URL | `https://<host>/api` |
| Formato | JSON (UTF-8) |
| Autenticación | `Authorization: Bearer <token>` (Sanctum) |
| Idioma de mensajes | Español (son la interfaz del usuario final) |
| Versionado | **No formalizado aún** — la versión vive en el prefijo `/api`; un `/api/v1` está en el [roadmap](../roadmap.md) |

## Superficies

| Prefijo | Audiencia | Autenticación |
|---|---|---|
| `/api/login`, `/api/register`, `/api/forgot-password`, `/api/reset-password`, `/api/check-email` | Público | Ninguna |
| `/api/system/announcements` | Público | Ninguna (devuelve anuncios globales vigentes) |
| `/api/auth/*` | Usuario autenticado | Token — **exento** del modo mantenimiento |
| `/api/<recurso>` | Usuario de empresa | Token + aislamiento de tenant + no mantenimiento |
| `/api/admin/*` | Operador de plataforma | Token + rol `super_admin` (sin contexto de tenant) |

## Sobre de respuesta

### Éxito con recurso

```json
{
  "success": true,
  "message": "Cliente creado exitosamente",
  "data": { "id": 1, "name": "Ana López" }
}
```

### Éxito con listado

```json
{
  "success": true,
  "data": [ { "id": 1, "name": "Ana López" } ],
  "meta": { "current_page": 1, "last_page": 3, "per_page": 15, "total": 42 }
}
```

`message` no se incluye en los listados. `meta` tiene siempre **exactamente** esas cuatro claves (ver [pagination-filtering-sorting.md](pagination-filtering-sorting.md)).

### Error de negocio

```json
{ "success": false, "message": "No tienes permiso para realizar esta acción" }
```

### Error de validación (422)

```json
{
  "message": "Los datos enviados no son válidos.",
  "errors": { "email": ["El campo email es obligatorio."] }
}
```

> Nota: el 422 conserva el formato nativo de Laravel (con `errors` por campo) y no usa el sobre `success`. Es una excepción deliberada de la convención, documentada en [error-responses.md](error-responses.md).

## Códigos HTTP

| Código | Uso |
|---|---|
| 200 | Lectura o actualización exitosa |
| 201 | Creación exitosa |
| 400 | Operación rechazada por el proveedor de un servicio (por ejemplo, broker de contraseñas) |
| 401 | Sin token, token inválido o sesión cerrada |
| 403 | Sin permiso, recurso perteneciente a otra empresa, usuario inactivo o rol insuficiente |
| 404 | Recurso inexistente |
| 409 | Conflicto de negocio (por ejemplo, impersonar un tenant sin usuarios) |
| 422 | Validación fallida |
| 503 | Empresa en modo mantenimiento |

## Convenciones de recursos

- **Rutas en inglés plural** (`/clients`, `/invoices`, `/expenses`), sin pluralizar prefijos compuestos (`/bank-accounts`, `/kanban/boards`).
- **Recursos anidados con guion**, no con rutas profundas: `/bank-accounts/{id}/movements`.
- **Borrado** con `DELETE`; las entidades con historial usan borrado lógico (soft delete) y las financieras, borrado físico.
- **Identificadores numéricos** salvo el tablero Kanban, que usa **UUID**.
- **El tenant nunca se recibe por URL ni payload**: `company_id` lo asigna el servidor.

## Parámetros comunes de listado

| Parámetro | Comportamiento |
|---|---|
| `page` | Página (inicia en 1) |
| `per_page` | Elementos por página; el default es 15 |
| `search` | Búsqueda `LIKE` en campos del recurso (nombre, RFC, etc.) |
| `status` | Filtro por estado, con vocabulario propio de cada recurso |

Detalle y vocabularios en [pagination-filtering-sorting.md](pagination-filtering-sorting.md).

## Límites y comportamientos

- **Sin rate limiting** implementado hoy (está en el [roadmap](../roadmap.md)).
- **Sin cabeceras de paginación HTTP** (`X-Total-Count` etc.): la paginación viaja en `meta`.
- **Sin CORS ampliado:** los orígenes permitidos se configuran por entorno y quedan restringidos a los dominios del frontend.
- **Compresión:** confiar en el servidor (Apache/Gzip) en producción.

## Errores comunes

| Causa | Respuesta |
|---|---|
| Token ausente o expirado | 401 |
| Recurso de otra empresa | 403 |
| Empresa en mantenimiento (rutas de negocio) | 503 con `maintenance: true` |
| Datos inválidos | 422 con `errors` por campo |
| ID inexistente | 404 |

Tabla completa y ejemplos en [error-responses.md](error-responses.md).
