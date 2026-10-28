# 0004. Convención de respuesta de la API: sobre `{success, data, meta}`

- **Estado:** ✅ Aceptada
- **Fecha:** 2026-06
- **Contexto:** La API es consumida por un frontend propio y, en el futuro, por terceros. Sin una convención única, cada endpoint responde distinto y el cliente termina con condicionales especiales. Hay que definir la forma de éxito, la de error y la paginación.

## Opciones evaluadas

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Sobre propio `{success, message, data, meta}`** (elegido) | El cliente distingue éxito/error sin inspeccionar códigos; permite mensajes al usuario en español; la paginación es uniforme | Duplica información que ya dan los códigos HTTP; hay que mantener la convención a mano |
| **JSON:API** | Estándar completo (recursos, relaciones, errores, paginación) | Muy pesado para un CRUD interno; su curva (compound documents, links) no compensa aquí |
| **Envoltorio Laravel Resources puro** | Integración nativa; fácil cambiar la forma del recurso | No unifica errores ni paginación; depende de que se use en todos los controllers |
| **Cruces por defecto de Laravel (sin sobre)** | Cero código | El cliente no puede distinguir "recurso sin datos" de "error"; los mensajes no llegan al usuario final |

## Decisión

Sobre propio, uniforme y documentado:

```json
{
  "success": true,
  "message": "Recurso guardado",
  "data": { }
}
```

- **Listados:** `{ "success": true, "data": [...], "meta": { "current_page", "last_page", "per_page", "total" } }` — cuatro claves fijas, construidas desde el paginador nativo, sin el bloque `links` completo.
- **Errores de negocio:** `{ "success": false, "message": "…" }` con el código HTTP apropiado (403, 409, 503).
- **Validación:** se respeta el formato nativo de Laravel (422 con `errors` por campo), sin envolver.
- **Mensajes en español:** son la interfaz directa con el usuario (el frontend los muestra en toasts).

Detalle completo en [../../api/conventions.md](../../api/conventions.md) y [../../api/error-responses.md](../../api/error-responses.md).

## Consecuencias

- ✅ El cliente puede tipar una sola forma genérica (`ApiEnvelope<T>`, `ApiListResponse<T>`) y reutilizarla en todos los servicios.
- ✅ Los mensajes llegan al usuario final sin traducción intermedia.
- ✅ La paginación es predecible: un componente de paginación funciona en cualquier listado.
- ⚠️ La convención se aplica a mano en cada controller (no hay trait base aún), por lo que pueden aparecer desviaciones puntuales — hay una iniciativa explícita de homogeneización en el [roadmap](../../roadmap.md).
- ⚠️ `success` y el código HTTP deben mantenerse coherentes; revisar ambos es parte de la definición de "terminado" de un endpoint.
