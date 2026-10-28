# 0001. Laravel como framework del backend

- **Estado:** ✅ Aceptada
- **Fecha:** 2026-05
- **Contexto:** Bloo necesita un backend para un ERP multi-tenant dirigido a PYMES mexicanas, con autenticación por token, roles granulares, CRUD intensivo y despliegue sencillo. El proyecto lo opera un desarrollador; la velocidad de iteración y el mantenimiento a futuro pesan tanto como el rendimiento.

## Opciones evaluadas

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Laravel (PHP 8.4)** | Ecosistema maduro para CRUD y autenticación; Sanctum y Spatie resuelven los problemas centrales (tokens y roles por equipo); despliegue barato en cualquier hosting PHP; curva de entrada corta | PHP tiene mala reputación injusta en círculos de backend moderno; el rendimiento por instancia es inferior al de runtimes asíncronos |
| **ASP.NET Core (C#)** | Rendimiento excelente, tipado estricto, arquitectura limpia por defecto | Curva operativa mayor para un proyecto individual; el costo de arranque (configuración, hosting) era mayor para el objetivo actual |
| **Node.js (NestJS/Express)** | Un solo lenguaje con el frontend; ecosistema npm; I/O ligero | El tipado en tiempo de ejecución es débil para reglas de negocio complejas; la validación y la autorización requieren más piezas manuales |
| **Django (Python)** | Admin generado, ORM sólido | El admin genérico no encaja bien con un modelo multi-tenant con permisos por equipo; el despliegue de Python añade fricción |

## Decisión

**Laravel**, en su versión 13, sobre PHP ≥ 8.4.

Los criterios que inclinaron la balanza fueron pragmáticos:

1. **Los dos problemas difíciles del proyecto ya están resueltos y probados en el ecosistema:** autenticación por token (Sanctum) y autorización por equipos (Spatie Permission con `teams`). Reconstruir ambos a mano en otro stack habría consumido semanas.
2. **CRUD intensivo con validación:** Laravel lo expresa en pocas líneas gracias a Eloquent y los FormRequests.
3. **Despliegue económico y simple:** el backend corre en una imagen ligera con Apache; no requiere runtime de JVM ni proceso Node persistente.
4. **Portabilidad de la plantilla:** la estructura (rutas, controllers, migraciones, seeders, pruebas) es reconocible por cualquier desarrollador PHP.

## Consecuencias

- ✅ Autenticación, autorización, validación, migraciones y pruebas resueltas con herramientas de primera clase.
- ✅ La suite de pruebas (PHPUnit con base en memoria) corre en integración sin infraestructura adicional.
- ⚠️ El lenguaje impone una arquitectura orientada a peticiones síncronas; las tareas largas (respaldos, reportes) deberán migrar a colas para no bloquear.
- ⚠️ Requiere PHP ≥ 8.4 en producción (la cadena Symfony 8 lo exige), lo que limita los hosts compatibles.
- ⚠️ El rendimiento por petición no es el del mercado; a escala se mitigará con caché, índices y asincronía, no cambiando de framework.
