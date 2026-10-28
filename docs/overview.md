# Visión general de Bloo

> Estado: ✅ Documento vivo — describe el estado actual del MVP (FASE 7 completada).

Bloo es un **ERP SaaS multi-tenant**: una única instalación de la plataforma atiende a múltiples empresas, cada una con sus datos aislados, sus usuarios, sus roles y su plan de suscripción.

## Actores

| Actor | Identificación | Alcance |
|---|---|---|
| **Usuario de tenant** | Token Bearer → `user.company_id` | Ve y opera **solo** los datos de su empresa |
| **Superadmin (operador)** | Token Bearer + rol `super_admin` | Administra la plataforma completa: tenants, planes, pagos, respaldos, auditoría |
| **Sistema** | — | Genera respaldos por tenant y registra eventos de auditoría |

No existen otros actores con acceso privilegiado. El superadmin **no** usa la aplicación ERP como cualquier usuario: opera desde rutas separadas (`/api/admin/*`).

## Dominios del producto

| Dominio | Contenido | Estado |
|---|---|---|
| **Organización** | Empresas (tenants), plan, suscripción, estado, modo mantenimiento | ✅ |
| **Identidad** | Usuarios, autenticación, roles y permisos por empresa | ✅ |
| **Catálogos de producto** | Productos (SKU, código de barras, precios, stock), marcas, categorías, unidades, almacenes, imágenes | ✅ |
| **Ventas** | Clientes (persona física / empresa / gobierno), facturas con ciclo de vida y folios automáticos | ✅ |
| **Finanzas** | Gastos, impuestos (IVA/ISR/IEPS/Retención), cuentas bancarias y movimientos | ✅ |
| **Trabajo** | Tablero Kanban: tableros, columnas y tarjetas con posición y asignación | ✅ |
| **Plataforma** | Planes, pagos de suscripción, respaldos por tenant, anuncios globales, auditoría del landlord, salud del sistema | ✅ |
| **RRHH, proyectos, CRM, marketing, logística** | ~107 permisos definidos y plantillas de interfaz | 📋 Planeados (sin backend) |
| **Presupuestos y flujo de caja** | Permisos y pantallas plantilla | 📋 Planeados |

> Los módulos RRHH/proyectos/CRM existen como **permisos y menús**, no como tablas o endpoints. Ver [requirements.md](requirements.md) para el detalle del estado.

## El Panel Landlord

Cara interna del SaaS, operada por el dueño de la plataforma:

- **Dashboard global:** totales de empresas, MRR (solo pagos efectivamente pagados), crecimiento, alertas y uso de recursos.
- **Gestión de tenants:** alta, edición, baja (borrado lógico), activación/desactivación y **modo mantenimiento por empresa**.
- **Impersonación:** el superadmin puede obtener un token temporal (1 hora) para operar dentro de un tenant como soporte — la acción queda registrada en auditoría.
- **Planes y pagos:** planes con límites (`limit_users`, `limit_products`), historial de pagos y renovación manual de suscripción.
- **Respaldos:** generación de un volcado SQL **por tenant** (filtrado por `company_id`), comprimido, con descarga protegida.
- **Auditoría y sistema:** log de acciones del landlord (con filtros), salud del sistema y visor de logs.

## Estado por capa

| Capa | Estado | Detalle |
|---|---|---|
| Backend (`erp-api`) | ✅ MVP funcional | Laravel 13, 77 pruebas / 345 assertions, suite verde |
| Frontend tenant (`erp-client`) | 🚧 Parcialmente conectado | Login, clientes, facturas, gastos, productos y anuncios consumen la API real; el resto son plantillas con datos simulados |
| Panel Landlord | ✅ Funcional | SPA Vue 3 embebida en el backend |
| Despliegue | ✅ Docker dev + prod | Imagen multi-etapa, sin dependencias de desarrollo |

### Pantallas del frontend conectadas a la API real

`/login`, `/products` (lista, detalle, crear, editar), `/clients`, `/invoices`, `/expenses` y el banner de anuncios del sistema (`GET /api/system/announcements`). El dashboard de inicio usa por ahora KPIs simulados en el propio frontend pendientes de conectar al endpoint `/api/dashboard/kpis`.

## Contexto regional

El MVP modela la realidad fiscal mexicana: RFC en clientes y empresas, impuestos tipificados (IVA, ISR, IEPS, retenciones), moneda por defecto MXN y fechas con huso horario por defecto `America/Mexico_City`. El modelo de datos no bloquea otros contextos: moneda e impuestos son campos por tenant.

## Próximos pasos

Ver [roadmap.md](roadmap.md) para el backlog priorizado y [architecture/decisions/](architecture/decisions/) para las decisiones que sustentan el diseño actual.
