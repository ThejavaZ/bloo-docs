# Decisiones arquitectónicas (ADR)

Este directorio registra las decisiones de diseño de Bloo mediante **Architecture Decision Records** (ADRs). Cada documento captura el problema, las opciones evaluadas, la decisión tomada y sus consecuencias — lo que permite entender *por qué* el sistema es como es, no solo *cómo* está hecho.

Convención: numeración secuencial, nombre en `kebab-case`, y la plantilla descrita en [CONTRIBUTING.md](../../../CONTRIBUTING.md). Un ADR se escribe después de decidir y se actualiza solo su **estado** (por ejemplo, al ser supersedida); el contexto y la decisión se preservan como registro histórico.

## Índice

| ADR | Decisión | Estado |
|---|---|---|
| [0001](0001-selection-of-backend-framework.md) | Laravel 13 como framework del backend | ✅ Aceptada |
| [0002](0002-database-strategy.md) | Base de datos relacional única (SQLite por defecto) | ✅ Aceptada |
| [0003](0003-tenant-isolation-strategy.md) | Aislamiento multi-tenant por `company_id` + equipos Spatie | ✅ Aceptada |
| [0004](0004-api-response-conventions.md) | Sobre de respuesta `{success, data, meta}` y mensajes en español | ✅ Aceptada |
| [0005](0005-frontend-split-and-auth-flow.md) | Frontend Next.js en repositorio separado y token en `localStorage` | ✅ Aceptada |
| [0006](0006-landlord-panel-embedded-spa.md) | Panel Landlord como SPA Vue 3 embebida en el backend | ✅ Aceptada |

## Qué no está en ADR todavía

Decisiones que se dieron por implícitas y aún no tienen registro (candidatas a formalizarse):

- Elección de Sanctum como mecanismo de autenticación (parte natural del stack Laravel).
- Spatie Permission como librería de roles (elección de paquete, no de arquitectura).
- Tailwind CSS y Jest en el frontend.
- Docker como única vía de despliegue documentada.
