# Manejo de errores

> Estado: ✅ Implementado. Estrategia pragmática: defaults del framework + sobre uniforme para errores de negocio.

## Filosofía

Bloo **no** personaliza en profundidad el manejo de excepciones del framework. En su lugar:

1. Se aprovechan los comportamientos por defecto de Laravel, que ya son correctos y JSON para rutas de API.
2. Los errores de **negocio** (sin permiso, empresa en mantenimiento, conflicto) se construyen explícitamente en el controller con el sobre `{success: false, message}`.
3. Los mensajes se escriben en **español**, porque son la interfaz directa con el usuario final vía toasts.

La ventaja: consistencia sin una capa intermedia que mantener. El costo: el sobre de validación (422) difiere ligeramente del de negocio, y conviene conocer ambas formas.

## Formatos de respuesta

| Situación | Código | Cuerpo |
|---|---|---|
| Éxito (recurso) | 200 / 201 | `{ "success": true, "message": "…", "data": {…} }` |
| Éxito (listado) | 200 | `{ "success": true, "data": [...], "meta": {…} }` |
| Error de validación | 422 | `{ "message": "…", "errors": { "campo": ["…"] } }` |
| No autenticado | 401 | `{ "message": "Unauthenticated." }` |
| Sin permiso / acceso cruzado | 403 | `{ "success": false, "message": "…" }` |
| Recurso inexistente | 404 | `{ "message": "…" }` |
| Conflicto de negocio | 409 | `{ "success": false, "message": "…" }` |
| Empresa en mantenimiento | 503 | `{ "success": false, "maintenance": true, "message": "…" }` |
| Error inesperado | 500 | Formato estándar del framework |

Ejemplos detallados en [../api/error-responses.md](../api/error-responses.md).

## Origen de cada tipo

### Errores del framework (sin intervención)

- **401** — cualquier ruta protegida sin token válido.
- **422** — validación de `$request->validate()` o FormRequests; el cuerpo es el formato estándar de Laravel.
- **404** — `ModelNotFoundException` al no encontrar un recurso por ID.
- **405/403 de método** — manejo del framework.

No hay personalizador de excepciones: `bootstrap/app.php` deja `withExceptions` vacío deliberadamente.

### Errores de negocio (construidos en el controller)

- **403** — recurso perteneciente a otra empresa, usuario inactivo, rol insuficiente.
- **409** — impersonación sobre un tenant sin usuarios elegibles, conflictos de unicidad no cubiertos por validación.
- **503** — modo mantenimiento del tenant (ver abajo).
- **400** — fallo del broker de contraseñas en recuperación.

## Modo mantenimiento por tenant

Cuando una empresa activa su modo mantenimiento, el middleware `ensure_not_maintenance` intercepta **todas** las rutas de negocio y responde:

```json
{
  "success": false,
  "maintenance": true,
  "message": "La empresa se encuentra en modo mantenimiento."
}
```

- **Código 503** (Servicio no disponible): es semánticamente correcto — el servicio existe pero está deliberadamente no disponible para ese tenant.
- **Exentas:** las rutas `/api/auth/*` (logout, perfil, cambio de contraseña) para que el usuario no quede atrapado.
- **El Panel Landlord** no pasa por este middleware: el operador debe poder atender la empresa justamente en ese estado.

> Nota de consistencia: parte de la documentación histórica del backend mencionaba 403 para mantenimiento; el comportamiento real y verificado por pruebas es 503. Alinear esa referencia está en el [roadmap](../roadmap.md).

## Errores de red en el frontend

La capa HTTP del cliente normaliza todos los errores a una forma única `{ status, message, …body }`, donde `status = 0` indica que no hubo respuesta (timeout o caída del backend). Con eso:

| Escenario | Comportamiento del cliente |
|---|---|
| 401 | Toast «Sesión expirada» (deduplicado), limpieza del token y redirección a `/login` |
| 403 | Toast «Acceso denegado» y redirección a `/forbidden` |
| 422 | El helper `getApiErrorMessage` muestra el primer mensaje de campo |
| 500 | Mensaje genérico en español; el detalle va a consola y al Error Boundary |
| 0 (sin respuesta) | Mensaje de indisponibilidad del servicio |

## Recomendaciones para nuevos endpoints

1. Usa el sobre `{success, message, data}` para éxito y `{success: false, message}` para negocio.
2. Deja que validación y 404 sigan siendo del framework: no dupliques formatos.
3. Un mensaje de error debe decirle al usuario **qué pasó y qué hacer**, no exponer detalles internos (nada de trazas ni SQL).
4. Nunca filtres datos de otro tenant devolviendo 404 en lugar de 403 sin pensarlo: 403 es más honesto y más fácil de monitorear.
