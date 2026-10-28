# Roadmap

> Estado: 📋 Documento de planificación. Refleja prioridades, no compromisos de fecha.

## Hito actual: MVP multi-tenant completo

Bloo tiene hoy un MVP funcional: backend con aislamiento verificado por pruebas, panel Landlord operativo y frontend parcialmente conectado. Las fases completadas hasta ahora:

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Núcleo multi-tenant: empresas, usuarios, roles y permisos | ✅ |
| 2 | Módulos MVP: catálogos, productos, clientes | ✅ |
| 3 | Módulo financiero: facturas, gastos, impuestos, bancos | ✅ |
| 4 | Panel Landlord: tenants, planes, dashboard | ✅ |
| 5 | Seguridad: modo mantenimiento por tenant, auditoría, revocación de tokens | ✅ |
| 6 | SaaS: pagos de suscripción, respaldos por tenant, anuncios del sistema | ✅ |
| 7 | Frontend conectado a la API: login, clientes, facturas, gastos, productos, anuncios | ✅ |

## Siguiente: consolidación del contrato de API

Antes de crecer en funcionalidades, endurecer lo que ya existe. Prioridad alta:

| Iniciativa | Motivo | Estado |
|---|---|---|
| Convención de ordenamiento (`?sort=campo:asc`) | Hoy no existe orden explícito; los listados dependen del orden por defecto de la BD | 📋 Ver [api/pagination-filtering-sorting.md](api/pagination-filtering-sorting.md) |
| Homogeneizar el sobre de respuesta | Algunos endpoints (como `/api/companies`) difieren del sobre `{success, data, meta}` | 📋 |
| Alinear el estado de mantenimiento documentado y devuelto | El backend responde 503; parte de la documentación histórica decía 403 | 📋 |
| Rate limiting en `/api/login` y recuperación de contraseña | Fuerza bruta y abuso del mailer | 📋 |
| Expiración/rotación de tokens | Los tokens no expiran por defecto | 📋 |
| Verificación de permisos por ruta en los módulos financieros | Hoy el aislamiento de tenant es la barrera principal; los permisos se refuerzan solo en algunos módulos | 📋 |
| Versionado de API (`/api/v1`) | Preparar evoluciones sin romper clientes | 📋 |

## Corto plazo: completar la experiencia de producto

| Iniciativa | Detalle | Estado |
|---|---|---|
| Conectar el dashboard a `/api/dashboard/kpis` | El frontend hoy simula KPIs localmente | 🚧 |
| Conectar el resto de pantallas a la API | ~47 rutas de UI existen; varias son plantillas con datos simulados | 🚧 |
| Presupuestos y flujo de caja | Permisos y menús ya definidos | 📋 |
| Notificaciones por correo (transaccionales) | El mailer está configurado como log; falta la capa de eventos | 📋 |
| 2FA | Columnas reservadas en `users` | 📋 |

## Medio plazo: operación como SaaS real

| Iniciativa | Detalle | Estado |
|---|---|---|
| Colas y jobs | La infraestructura existe (tablas + driver `database`); se necesita la primera tarea asíncrona (respaldos, correos, reportes) | 📋 |
| Respaldos automáticos programados | Hoy la generación es manual y síncrona desde el Panel Landlord | 📋 |
| Resolución de tenant por dominio | El campo `domain` existe en `companies`; falta el middleware de resolución | 📋 |
| Límites de plan aplicados | `limit_users` y `limit_products` están en el modelo; falta la validación en creación | 📋 |
| Migración a MySQL/PostgreSQL en producción | SQLite es el default; el salto requiere plan de migración y pruebas de carga | 📋 |
| Métricas y monitoreo | Salud del sistema existe; falta telemetría (latencia, errores, uso por tenant) | 📋 |

## Largo plazo: expansión de dominio

Módulos ya previstos en el modelo de permisos (~107 permisos, ~18 módulos) sin backend aún:

- **RRHH:** empleados, asistencia, nómina, reclutamiento, evaluaciones, contratos, vacaciones.
- **Proyectos y tareas** (más allá del Kanban actual).
- **CRM:** leads, oportunidades, servicio al cliente, quejas.
- **Marketing:** campañas, redes sociales, SEO, email marketing.
- **Logística:** almacenes avanzados, envíos, entregas, cadena de suministro.
- **Servicios:** reparaciones, mantenimiento, garantías.
- **Documentos, calendario, políticas y capacitación.**

> El orden de ejecución se decidirá con base en demanda real; estos módulos están **previstos**, no comprometidos.

## Criterios de evolución de esta documentación

- Cada cambio de arquitectura relevante genera o actualiza un [ADR](architecture/decisions/).
- Cuando una funcionalidad pase de 📋 a ✅, se actualiza su fila en [requirements.md](requirements.md) y el estado en [overview.md](overview.md).
- Este roadmap se revisa al cerrar cada fase.
