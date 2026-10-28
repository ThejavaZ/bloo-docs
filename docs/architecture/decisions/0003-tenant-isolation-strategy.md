# 0003. Aislamiento multi-tenant por `company_id` con equipos Spatie

- **Estado:** ✅ Aceptada
- **Fecha:** 2026-06
- **Contexto:** Decision central de Bloo. La plataforma atiende a muchas empresas desde un solo despliegue; un fallo de aislamiento es un incidente de privacidad grave. Hay que elegir cómo separar los datos, cómo identificar el tenant en cada petición y cómo modelar roles que pertenecen a una empresa.

## Opciones evaluadas

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Base de datos compartida + columna `company_id`** (elegida) | Operación trivial (un despliegue, una BD); migraciones únicas; costo mínimo; consultas cruzadas del Landlord directas | El aislamiento depende de la disciplina del código; un `where` faltante es un fallo potencial; sin escalamiento por tenant |
| **Base de datos por tenant** | Aislamiento físico fuerte; respaldo por tenant nativo | Migraciones N veces; sobrecosto operativo muy alto para PYMES; conexiones por tenant |
| **Esquema por tenant (PostgreSQL)** | Aislamiento lógico-fuerte con una sola instancia | Ata el proyecto a PostgreSQL desde el día uno; la complejidad de migraciones multi-esquema es alta |
| **Paquete de tenancy (stancl/tenancy u homólogo)** | Resuelve resolución por dominio, BDs separadas y caches por tenant | Añade una abstrucción pesada para un caso que hoy necesita solo filtros por columna; sobrediseño para el MVP |
| **Aislamiento en la capa de conexión (schemas compartidos multi-DB)** | Transparente para los controllers | Poca flexibilidad para el panel Landlord y los respaldos; difícil de depurar |

## Decisión

**Base de datos compartida con `company_id` explícito en cada tabla de negocio**, identificación del tenant desde el **token** (no desde el dominio) y roles modelados con **Spatie Permission en modo teams** (`team_id = company_id`).

Elementos de la decisión:

1. **El tenant se resuelve por el token:** token → usuario → `company_id`. Nada en la URL determina el alcance de los datos.
2. **Filtrado explícito en controllers**, sin scopes globales ocultos: cada endpoint hace visible su condición de aislamiento.
3. **Unicidades compuestas** (`company_id` + SKU / RFC / folio / código) para que la unicidad sea relativa al tenant.
4. **Roles por equipo:** un rol existe solo dentro de su empresa; el middleware `set_team_context` fija el equipo en cada petición.
5. **El Landlord es la excepción explícita:** rutas `/api/admin/*` sin contexto de equipo, protegidas por rol y auditadas.

## Consecuencias

- ✅ Operación y costo mínimos: un despliegue atiende toda la plataforma.
- ✅ El aislamiento es **verificable por pruebas**: la suite tiene casos dedicados de accesos cruzados y de respaldos por tenant.
- ✅ El superadmin puede operar globalmente (dashboard, auditoría, respaldos) sin atajos frágiles.
- ⚠️ El aislamiento es responsabilidad del código: obliga a que cada endpoint nuevo repita el patrón (filtrar, verificar propiedad, asignar en servidor). Es el precio de no usar paquetes opacos.
- ⚠️ Sin escalamiento por tenant: una empresa de consumo intensivo afecta a las demás. Mitigable con caché, índices y, si acaso, particionado futuro.
- ⚠️ Una futura resolución por dominio (campo `domain` ya reservado) requerirá un middleware adicional; la decisión no lo bloquea.

## Referencias internas

- [Modelo de tenancy](../tenancy-model.md)
- [Aislamiento de tenants y su cobertura de pruebas](../../security/tenant-isolation.md)
