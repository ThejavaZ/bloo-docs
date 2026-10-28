# Logging y auditoría

> Estado: ✅ Implementado (canales y auditoría de Landlord) · 🚧 Falta redacción de PII y retención definida.

## Canales de log

El backend usa el sistema de logs de Laravel con la configuración por defecto del proyecto:

| Entorno | Canal | Destino |
|---|---|---|
| Desarrollo | `stack`/`single` | `storage/logs/laravel.log` |
| Producción (Docker) | `stack` con salida a `stderr` | Lo captura el runtime de contenedores |

Los canales disponibles (configurables por entorno) incluyen `single`, `stack`, `daily`, `stderr` y `syslog`. No se han definido canales personalizados todavía: todo lo que emite la aplicación llega al canal principal.

### Qué se registra

- Errores y excepciones no capturadas (nivel `error`).
- Eventos del framework (deprecaciones, advertencias).
- Recuperación de contraseñas (el mailer en desarrollo escribe el correo al log).
- Sin logs de peticiones exitosas ni de cuerpos de petición — no hay *request logging* implementado.

## Auditoría de autenticación

La tabla `user_logins` registra cada intento de login con **fecha, IP y resultado**. Es la base para detectar:

- Fuerza bruta contra una cuenta.
- Accesos desde ubicaciones inesperadas.
- Cuentas con intentos fallidos repetidos.

## Auditoría del Landlord (`admin_audit_logs`)

Todo lo que el operador de plataforma hace sobre tenants y planes queda registrado con:

| Campo | Contenido |
|---|---|
| `admin_user_id` | Quién ejecutó la acción |
| `action` | Código de acción, por ejemplo `tenant.created` |
| `target_company_id` | Sobre qué empresa recaía la acción |
| `ip_address` | Origen |
| `details_json` | Detalle estructurado (por ejemplo, valores anteriores y nuevos al editar un plan) |

### Acciones registradas

| Familia | Acciones |
|---|---|
| Tenants | `tenant.created`, `tenant.deleted`, `tenant.status_changed` |
| Mantenimiento | `tenant.maintenance_enabled`, `tenant.maintenance_disabled` |
| Soporte | `tenant.impersonate`, `tenant.tokens_revoked` |
| Respaldos | `tenant.backup_created`, `tenant.backup_downloaded` |
| Planes | `plan.updated` (con los cambios de antes/después) |

La auditoría se consulta desde el panel con filtros por `action`, `target_company_id` y rango de fechas (`from`/`to`).

### Principios de la auditoría

- **No se puede omitir:** el registro ocurre en el flujo de la acción, no se delega al cliente.
- **Inmutable por diseño de aplicación:** no hay endpoints de edición o borrado de auditoría.
- **Las impersonaciones siempre dejan rastro**, precisamente porque son el acceso más sensible.

## Visor de logs del sistema

El Landlord expone `GET /api/admin/system/logs`, que parsea el archivo de log activo para su inspección desde el panel, junto con `GET /api/admin/system/health` (estado de la base de datos, disco y tiempo de respuesta).

> Ambos endpoints exigen rol `super_admin` y exponen contenido interno del servidor; no deben ampliarse a otros roles.

## Salud del sistema

`/api/admin/system/health` devuelve comprobaciones de:

- Conectividad y respuesta de la base de datos.
- Espacio y escritura en disco.
- Versión de PHP y de Laravel.

Es la base sobre la que se podrá construir monitoreo externo en el futuro.

## Pendientes

| Iniciativa | Motivo | Estado |
|---|---|---|
| Redacción de PII en logs | Evitar que nombres, correos o montos queden en texto plano a largo plazo | 📋 |
| Retención y rotación definidas | Hoy depende de la configuración por defecto (archivo diario simple) | 📋 |
| Request logging con correlación (ID de petición) | Facilita seguir una operación end-to-end entre frontend y backend | 📋 |
| Canal específico de auditoría separado del log de aplicación | Fortalece la inmutabilidad percibida y facilita la exportación | 📋 |
| Alertas sobre eventos de seguridad (logins fallidos masivos, impersonaciones) | Pasar de registrar a reaccionar | 📋 |
| Métricas por tenant (latencia, errores, uso) | Soporte y dimensionamiento | 📋 |

## Reglas para nuevos eventos

1. **Nunca** registres tokens, contraseñas, cabeceras `Authorization` ni payloads completos.
2. Usa códigos de acción puntuales (`recurso.acción`) en auditoría, no frases libres, para poder filtrar.
3. Registra el **antes y el después** en cambios sensibles (como ya hace `plan.updated`).
4. Si un evento es crítico para la seguridad, su registro es parte de la definición de "terminado", no un extra.
