# Modelo de multi-tenancy

> Estado: ✅ Implementado. Un solo despliegue, una sola base de datos, aislamiento lógico por `company_id`.

## Decisión en una línea

**Base de datos compartida con columna `company_id` en cada tabla de negocio**, sin esquemas separados ni bases de datos por tenant. El tenant se resuelve desde el token de autenticación, no desde el dominio.

## Identificación del tenant

El flujo es siempre el mismo y no depende de la URL:

```text
Bearer token  →  personal_access_tokens  →  user  →  user.company_id  →  contexto
```

1. El cliente envía `Authorization: Bearer <token>`.
2. Sanctum resuelve el usuario dueño del token.
3. `user.company_id` es la **única** fuente de verdad del tenant.
4. Los controllers consultan y filtran con ese valor.

> No existe resolución por subdominio ni por header. El campo `domain` existe en la tabla `companies` como preparación futura, pero hoy no participa en el encaminamiento (ver [roadmap](../roadmap.md)).

## Cadena de middleware

Las rutas de negocio usan esta pila (`erp-api/erp/routes/api.php`):

| # | Middleware (alias) | Responsabilidad | Respuesta al fallar |
|---|---|---|---|
| 1 | `auth:sanctum` | Resuelve el usuario desde el token | 401 `{message: "Unauthenticated."}` |
| 2 | `set_team_context` | Fija el contexto de equipos de Spatie con `company_id` del usuario | — (solo si hay usuario con empresa) |
| 3 | `ensure_not_maintenance` | Consulta si la empresa está en modo mantenimiento | 503 `{success:false, maintenance:true, message}` |

Excepciones de la pila:

- **`/api/auth/*`** (perfil, cambio de contraseña, logout) queda **exento** del bloqueo por mantenimiento, para que el usuario pueda cerrar sesión aunque su empresa esté congelada.
- **`/api/admin/*`** (Landlord) no pasa por `set_team_context` ni por `ensure_not_maintenance`: el superadmin debe poder operar precisamente cuando una empresa está en mantenimiento. Se protege con `auth:sanctum` + `ensure_superadmin`.

## Aislamiento en los controllers

No hay *scopes* globales ni paquete de tenancy: el filtrado es **explícito en cada controller**. El patrón es siempre el mismo:

```php
// Listado — solo registros de mi empresa
Client::where('company_id', $request->user()->company_id)->paginate(15);

// Detalle / edición / baja — verificación de propiedad
if ($client->company_id !== $request->user()->company_id) {
    return response()->json(['success' => false, 'message' => '…'], 403);
}

// Alta — el server fija el tenant, nunca confía en el cliente
Client::create([...$data, 'company_id' => $request->user()->company_id]);
```

Tres reglas se repiten en todos los módulos:

1. **Filtrar** todo listado por `company_id`.
2. **Verificar** propiedad antes de leer, editar o borrar un recurso por ID.
3. **Asignar** `company_id` en el servidor al crear; el valor nunca viene del payload.

### Unicidad relativa al tenant

Las restricciones únicas son **compuestas**, para que dos empresas puedan tener los mismos valores sin chocar:

| Tabla | Unicidad compuesta |
|---|---|
| `users` | `(email, company_id)` — el correo es único por empresa, no global |
| `products` | `(company_id, sku)` |
| `clients` | `(company_id, rfc)` |
| `invoices` | `(company_id, invoice_number)` |
| `taxes` | `(company_id, code)` |

## Relación con roles y permisos

Spatie Permission opera en modo **teams**: `team_id = company_id` y `guard_name = 'api'`. Los roles de un usuario existen únicamente dentro de su empresa. El middleware `set_team_context` fija ese equipo antes de cualquier verificación de rol o permiso.

Detalle en [authentication-and-authorization.md](authentication-and-authorization.md).

## Relación con el Landlord

El Panel Landlord es la **excepción deliberada**: sus rutas no fijan equipo, de modo que las consultas del superadmin no se filtran por empresa. Es un superpoder explícito, acotado a `/api/admin/*` y verificado por el middleware `ensure_superadmin`, y todas sus acciones quedan en el log de auditoría (ver [../security/tenant-isolation.md](../security/tenant-isolation.md)).

## Respaldo por tenant

Aunque los datos conviven en una base, el respaldo del Landlord genera un volcado **por empresa**: se recorren las tablas que tienen la columna `company_id` y se extraen solo las filas del tenant, conservando la cadena de claves foráneas. El resultado se comprime y se almacena fuera del alcance del cliente web.

## Consecuencias de la decisión

| A favor | En contra / a vigilar |
|---|---|
| Cero operación por tenant: un despliegue, una BD, un respaldo global | Un error de filtrado afectaría la privacidad entre tenants — por eso el aislamiento tiene [pruebas dedicadas](../security/tenant-isolation.md#cubierta-de-pruebas) |
| Migraciones y actualizaciones únicas para toda la plataforma | Sin escalamiento por tenant (una empresa enorme pesa sobre todas) |
| Costo inicial mínimo (SQLite arranca sin configuración) | El respaldo individual requiere lógica propia (ya implementada) |
| Migrar a MySQL/PostgreSQL no toca el modelo | Un tenant con consultas pesadas puede afectar el rendimiento compartido |

## Verificación

El aislamiento está verificado por la suite de pruebas: listados filtrados, 403 en accesos cruzados para clientes, facturas, gastos, impuestos, productos, cuentas bancarias y usuarios; el Landlord sin filtro de equipo; y el respaldo que contiene solo datos del tenant pedido.

Diagrama fuente: [../../diagrams/tenancy-model.mmd](../../diagrams/tenancy-model.mmd).
