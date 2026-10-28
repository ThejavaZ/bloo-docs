# 0006. Panel Landlord como SPA Vue 3 embebida en el backend

- **Estado:** ✅ Aceptada
- **Fecha:** 2026-10
- **Contexto:** La plataforma necesita una cara de administración global (tenants, planes, pagos, respaldos, auditoría) accesible solo para el operador (`super_admin`). Hay que decidir dónde vive esa interfaz y con qué tecnología, sabiendo que su audiencia es una sola persona o equipo, con frecuencia de uso baja pero exigencias de seguridad altas.

## Opciones evaluadas

| Opción | Ventajas | Desventajas |
|---|---|---|
| **SPA Vue 3 compilada con Vite, servida por el propio backend** (elegida) | Un solo despliegue y un solo origen (sin CORS); la interfaz comparte release y versionado con la API a la que administra; bajo costo de mantenimiento para pocos usuarios | Dos stacks de frontend en el proyecto (Next y Vue); la compilación añade un paso al build del backend |
| **Módulos dentro del frontend Next.js (con roles)** | Un solo frontend | Expone la superficie de administración en la misma app que usan los clientes; los permisos de UI serían la única barrera visual; acopla release de plataforma con release de producto |
| **Blade + Livewire (server-rendered)** | Cero build, integración nativa | Menos inmediata para tableros con filtros, tablas y métricas en vivo |
| **Aplicación separada (otro servicio/origen)** | Aislamiento total | Un despliegue y un origen más que operar para una UI interna; CORS extra; beneficio de seguridad marginal frente a una ruta protegida por rol |

## Decisión

El Panel Landlord es una **SPA Vue 3 + TypeScript compilada con Vite, embebida en el backend Laravel** y servida desde `/admin`. Sus peticiones consumen `/api/admin/*`, protegidas por `auth:sanctum` + middleware `ensure_superadmin`, **sin** contexto de tenant.

Elementos complementarios de la decisión:

- **Auditoría obligatoria:** cada acción sensible del panel queda registrada (`tenant.created`, `tenant.impersonate`, `plan.updated`…) con usuario, IP y detalle.
- **Impersonación con TTL:** soporte remoto emite un token temporal de 1 hora, no una sesión permanente.
- **Superficie separada:** el panel no comparte rutas ni componentes con la app de clientes.

## Consecuencias

- ✅ Un solo despliegue y un solo origen: sin configuración CORS adicional y sin segundo servicio que operar.
- ✅ La UI del Landlord se versiona junto con la API que administra; no hay riesgo de que un despliegue desalineado rompa el panel.
- ✅ La superficie de administración no está expuesta en la aplicación pública de clientes: un fallo de permisos de UI en el frontend de producto no puede llegar al panel.
- ⚠️ El proyecto mantiene dos ecosistemas de frontend (Next.js y Vue). Se aceptó el costo a cambio de la separación de superficies.
- ⚠️ El paso de compilación de Vite participa en el build del backend; el Docker de producción lo resuelve con imagen multi-etapa.
- ⚠️ El panel hereda el ciclo de releases del backend: una corrección de UI obliga a redesplegar la API.
