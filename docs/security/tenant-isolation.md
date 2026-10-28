# Aislamiento de tenants

> Estado: ✅ Implementado y verificado por pruebas. Este es el documento de seguridad central de Bloo.

El compromiso fundamental de Bloo: **ninguna empresa puede ver, modificar ni exportar los datos de otra**, ni siquiera por descuido de una implementación. Este documento describe las capas de defensa que lo garantizan.

## Principio

El aislamiento no depende de una sola barrera. Se apoya en cuatro capas: **identificación por token**, **filtros explícitos**, **límites de unicidad** y **pruebas de regresión**.

## Capa 1 — El tenant sale del token, no del cliente

```text
Authorization: Bearer <token>
        ↓
personal_access_tokens → user
        ↓
user.company_id   ← única fuente de verdad
```

- El `company_id` **nunca** se acepta desde la URL, el body ni headers.
- El servidor lo asigna al crear registros y lo usa para filtrar lecturas.
- Un token no puede "elegir" empresa: su alcance es el del usuario dueño del token.

## Capa 2 — Filtrado y verificación en cada endpoint

Todo endpoint de negocio repite el patrón:

| Operación | Regla | Ante la violación |
|---|---|---|
| Listado | `WHERE company_id = usuario.company_id` | — (el filtro es la defensa) |
| Lectura / edición / baja por ID | Verificación explícita de propiedad | 403 |
| Alta | `company_id` asignado en el servidor | — |

No hay *scopes* globales ocultos: cada endpoint hace visible su condición de aislamiento, lo que la revisión de código puede auditar línea por línea.

## Capa 3 — Unicidades compuestas por tenant

Las restricciones únicas son `(company_id, campo)`, de modo que la base de datos rechaza colisiones **dentro** de una empresa sin impedir la homonimia **entre** empresas:

| Tabla | Unicidad |
|---|---|
| `users` | `(email, company_id)` |
| `products` | `(company_id, sku)` |
| `clients` | `(company_id, rfc)` |
| `invoices` | `(company_id, invoice_number)` |
| `taxes` | `(company_id, code)` |

Esto también impide un ataque clásico de registro: crear un usuario con el correo de un administrador de otra empresa no otorga nada, porque el correo es único solo dentro del propio tenant.

## Capa 4 — Pruebas de regresión

El aislamiento está escrito como suite de pruebas que corre en cada cambio:

| Garantía | Prueba |
|---|---|
| El listado de clientes solo contiene los de la empresa del usuario (con búsqueda) | ✅ |
| No se puede editar un cliente de otra empresa (403) | ✅ |
| Lo mismo aplica a facturas, gastos, impuestos, productos, cuentas bancarias y usuarios | ✅ |
| El superadmin del Landlord ve todos los tenants **sin** filtro de equipo | ✅ |
| El respaldo generado de un tenant contiene **solo** sus datos | ✅ |
| El modo mantenimiento bloquea rutas de negocio pero no `/auth` ni el Landlord | ✅ |

Cualquier cambio que toque un filtro de tenant debe acompañarse de una prueba equivalente.

## La excepción del Landlord

El Panel Landlord opera sin contexto de empresa. Es un superpoder **explícito y acotado**:

- Solo accesible con rol `super_admin` (middleware dedicado, probado).
- Sus acciones quedan registradas en `admin_audit_logs` (quién, qué, a qué empresa, IP).
- La impersonación emite un token temporal de **1 hora**, no una sesión abierta, y también se audita.

## Respaldo por tenant

El respaldo se genera **filtando por `company_id`** a nivel de aplicación: se recorren las tablas con columna de empresa y se extraen solo las filas del tenant, preservando la cadena de claves foráneas. Una prueba verifica que el volcado de un tenant no contenga datos de otro.

La descarga valida el nombre de archivo con una expresión regular estricta, evitando *path traversal* hacia otros archivos del servidor.

## Límites de la estrategia

Honestidad sobre lo que esta aproximación **no** cubre todavía:

| Límite | Estado |
|---|---|
| La barrera es el código de aplicación, no el motor de BD. Un endpoint nuevo sin filtro sería un fallo | Mitigado por convención + pruebas; candidato a *scopes* globales compartidos en el futuro |
| Sin rate limiting: un ataque de fuerza bruta contra login no está frenado | 📋 En el [roadmap](../roadmap.md) |
| Tokens sin expiración automática: un token robado es válido hasta que se revoque | 📋 En el [roadmap](../roadmap.md); mitigado por revocación manual y por tenant |
| Sin cifrado a nivel de columna para datos sensibles selectos | Fuera del alcance actual del MVP |
| El rendimiento es compartido: un tenant con consultas pesadas afecta a todos | Conocido; mitigable con caché e índices |

## Reglas para quienes implementan

1. **Toda consulta de negocio nace con `company_id`.** Sin excepción, sin "solo esta vez".
2. **Nunca confíes en el payload para el alcance.** El tenant viene del token.
3. **Toda prueba de un endpoint nuevo incluye el caso cruzado:** usuario de la empresa B intentando acceder al recurso de la empresa A.
4. **Si expones un filtro nuevo, valida que no sea un canal cruzado** (por ejemplo, `?company_id=` en el query).
5. **Ante duda entre 403 y 404, usa 403** y regístralo en monitoreo.
