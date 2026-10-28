# 0002. Estrategia de base de datos: relacional única con SQLite por defecto

- **Estado:** ✅ Aceptada
- **Fecha:** 2026-05
- **Contexto:** Bloo debe persistir datos transaccionales de muchas empresas en una sola plataforma. Hay que elegir motor de datos, estrategia de esquemas y punto de partida para el despliegue, con la restricción de que un solo desarrollador debe poder operar el proyecto sin infraestructura cara.

## Opciones evaluadas

| Opción | Ventajas | Desventajas |
|---|---|---|
| **SQLite por defecto + compatible MySQL/PostgreSQL** | Arranca con cero configuración; perfecto para desarrollo y MVP; un solo archivo respalda fácilmente; migrar después = cambiar `.env` | Escrituras concurrentes limitadas frente a cargas altas; algunas funciones SQL varían entre motores |
| **MySQL/MariaDB desde el inicio** | Consolidado para apps PHP; maneja concurrencia real | Obliga a instalar y operar un servidor incluso en desarrollo; fricción para contribuir o clonar y probar |
| **PostgreSQL desde el inicio** | El más robusto técnicamente; excelentes tipos JSON y PostGIS | Igual fricción operativa inicial; exige disciplina de tipos (enums, arrays) desde el día uno |
| **NoSQL (MongoDB)** | Flexibilidad de esquema | El dominio ERP es transaccional y relacional por definición (clientes → facturas → pagos); un modelo documental complicaría la integridad |

## Decisión

**Modelo relacional con SQLite como motor por defecto**, manteniendo el código compatible con MySQL y PostgreSQL a través de la configuración de entorno.

- Migraciones y consultas escritas con la API de Eloquent, evitando SQL específico de motor.
- El despliegue de producción Docker usa SQLite con persistencia en volumen, para que el MVP no dependa de un servidor de base de datos externo.
- Las tablas de caché, sesiones y trabajos usan el mismo motor (tablas estándar de Laravel), eliminando dependencias adicionales.

## Consecuencias

- ✅ `git clone` + `composer install` + un archivo vacío = entorno funcionando. Cero fricción para desarrollo y pruebas.
- ✅ Las pruebas corren sobre SQLite en memoria: rápidas y aisladas por ejecución.
- ✅ La ruta de migración a MySQL/PostgreSQL está abierta sin tocar el modelo (cambiar variables de entorno).
- ⚠️ La concurrencia de escritura de SQLite es un techo operativo; el salto a MySQL/PostgreSQL antes de producción multi-tenant real está en el [roadmap](../../roadmap.md).
- ⚠️ Se debe evitar SQL propietario; algunas optimizaciones de índice diferirán entre motores.
- ⚠️ El respaldo por tenant se implementó a nivel de aplicación (volcado filtrado por `company_id`) precisamente porque no se puede confiar en herramientas de dump nativas del motor.
