# Modelo de amenazas

> Estado: ✅ Documento vivo. Cubre el alcance del MVP; se revisa al añadir superficies nuevas (pagos, APIs de terceros, dominios propios).

Metodología simplificada (adaptación ligera de STRIDE) centrada en lo que un ERP multi-tenant realmente debe resistir.

## Activos

| Activo | Dónde vive | Impacto de un compromiso |
|---|---|---|
| Datos de negocios de cada tenant | Base de datos compartida | Máximo: fuga de información comercial entre empresas |
| Credenciales y tokens | `users` (hash bcrypt), `personal_access_tokens` (hash) | Acceso no autorizado a la plataforma |
| Roles y permisos | Tablas Spatie con `team_id` | Escalada de privilegios dentro o entre empresas |
| Panel Landlord | Rutas `/api/admin/*` | Control total de la plataforma (todos los tenants) |
| Respaldos | `storage/app/backups` | Exfiltración masiva de datos por tenant |
| Configuración (claves, SMTP, credenciales de BD) | Variables de entorno | Compromiso total del despliegue |
| Logs y auditoría | `storage/logs`, `admin_audit_logs` | Pérdida de trazabilidad o fuga de datos en logs |

## Límites de confianza

```text
[ Navegador del usuario ]  ──HTTPS──▶  [ API Laravel ]  ──▶  [ Base de datos ]
[ Navegador del operador ] ──HTTPS──▶  [ /api/admin/* ] ──▶  [ Base de datos ]
                                        │
                                        └──▶ [ Disco: respaldos y logs ]
```

- Todo lo que cruza el límite navegador↔API viaja con token Bearer; la confianza se establece por usuario, no por red.
- El panel Landlord comparte origen con la API, pero su autorización es por rol, no por red.
- El acceso a disco (respaldos, logs) está fuera del alcance del cliente web; la descarga de respaldos pasa por validación de nombre de archivo.

## Amenazas y mitigaciones

### T1 — Aislamiento entre tenants roto (IDOR / filtración horizontal)

| | |
|---|---|
| **Escenario** | Un usuario autenticado de la empresa A accede por ID a recursos de la empresa B, o un listado no filtra correctamente |
| **Impacto** | Fuga o alteración de datos entre empresas — el fallo más grave posible en un SaaS |
| **Mitigación** | Token→`company_id` como única fuente; verificación de propiedad en cada endpoint; unicidades compuestas; **suite de pruebas de aislamiento** que simula el acceso cruzado en todos los módulos |
| **Estado** | ✅ Cubierto y probado · ver [tenant-isolation.md](tenant-isolation.md) |

### T2 — Escalada de privilegios dentro del tenant

| | |
|---|---|
| **Escenario** | Un empleado obtiene permisos de administrador, o un usuario se autoasigna roles |
| **Mitigación** | Los roles se gestionan desde endpoints con `role_or_permission`; los permisos se evalúan contra el equipo del usuario; el frontend oculta menús sin permiso (comodidad, no seguridad) |
| **Estado** | 🚧 La verificación por ruta se refuerza progresivamente (ver [roadmap](../roadmap.md)) |

### T3 — Escalada hacia el rol de plataforma (superadmin)

| | |
|---|---|
| **Escenario** | Un usuario de tenant alcanza rutas `/api/admin/*` |
| **Mitigación** | Middleware `ensure_superadmin` en todas las rutas del panel; sin el rol, 403; las rutas del Landlord no comparten grupo con las de negocio |
| **Estado** | ✅ Cubierto y probado |

### T4 — Robo o abuso de tokens

| | |
|---|---|
| **Escenario** | Token filtrado (XSS, dispositivo perdido, logs) o creación masiva de tokens |
| **Mitigación** | Tokens guardados hasheados; revocación individual (`logout`), por usuario (`revoke-tokens`) y **por tenant desde el Landlord**; cambio de contraseña revoca las demás sesiones; el token de impersonación caduca en 1 hora |
| **Pendiente** | Expiración automática y rotación — en el [roadmap](../roadmap.md) |
| **Estado** | 🚧 Parcialmente cubierto |

### T5 — Fuerza bruta contra autenticación

| | |
|---|---|
| **Escenario** | Intentos masivos de contraseña contra `/api/login` o abuso de `/api/forgot-password` (costo de correo, denegación) |
| **Mitigación** | El broker de contraseñas aplica límite de reintentos; los intentos quedan registrados en `user_logins` (fecha, IP, resultado) |
| **Pendiente** | Rate limiting explícito por IP y por cuenta |
| **Estado** | 🚧 Parcialmente cubierto |

### T6 — Inyección y validación insuficiente

| | |
|---|---|
| **Escenario** | SQL inyectado, campos no validados, payloads maliciosos |
| **Mitigación** | Eloquent parametriza las consultas; validación server-side en todos los endpoints (422); el frontend no es la barrera |
| **Estado** | ✅ Cubierto por diseño del framework |

### T7 — Exposición de secretos en el repositorio o la imagen

| | |
|---|---|
| **Escenario** | `APP_KEY`, credenciales de BD o SMTP versionadas o embebidas en la imagen Docker |
| **Mitigación** | Todo por variables de entorno; la imagen de producción se construye sin `.env`; el historial de Git del repositorio de documentación se revisó antes de publicarse; esta documentación no contiene valores reales |
| **Estado** | ✅ Cubierto |

### T8 — Path traversal en descarga de respaldos

| | |
|---|---|
| **Escenario** | Solicitar `/admin/backups/../../.env` o rutas arbitrarias |
| **Mitigación** | El nombre de archivo se valida con expresión regular antes de resolver la ruta; solo se aceptan los nombres que el propio sistema generó |
| **Estado** | ✅ Cubierto |

### T9 — Exfiltración vía respaldos

| | |
|---|---|
| **Escenario** | Un respaldo de la empresa A contiene datos de la empresa B |
| **Mitigación** | El volcado filtra por `company_id` a nivel de aplicación; **prueba dedicada** que verifica que el contenido sea exclusivo del tenant |
| **Estado** | ✅ Cubierto y probado |

### T10 — Datos sensibles en logs

| | |
|---|---|
| **Escenario** | Tokens, contraseñas o datos de negocio quedan escritos en `storage/logs` |
| **Mitigación** | Los logs registran eventos, no cuerpos de petición completos; la recuperación de contraseña no escribe credenciales; en producción el log va a `stderr` para capturarlo fuera del contenedor |
| **Pendiente** | Revisión periódica y redacción explícita de PII al escalar |
| **Estado** | 🚧 Vigilancia continua |

### T11 — Denegación de servicio por un tenant

| | |
|---|---|
| **Escenario** | Consultas pesadas o abusos de un tenant degradan la plataforma compartida |
| **Mitigación** | Paginación obligatoria en listados; caché configurable; modo mantenimiento por tenant como cortafuegos operativo |
| **Pendiente** | Rate limiting y métricas por tenant |
| **Estado** | 🚧 Parcialmente cubierto |

### T12 — Compromiso del modo mantenimiento

| | |
|---|---|
| **Escenario** | Un tenant en mantenimiento sigue escribiendo datos, o el bloqueo se salta |
| **Mitigación** | El middleware intercepta toda ruta de negocio; solo `/api/auth/*` queda exento (deliberadamente, para no atrapar usuarios); verificado por prueba |
| **Estado** | ✅ Cubierto |

## Superficies fuera de alcance hoy

- **Pasarelas de pago:** los pagos se registran manualmente; al integrarse, requerirá un ADR y un modelo de amenazas propio.
- **APIs para terceros / webhooks:** no existen aún.
- **Multi-dominio (`domain` por tenant):** añade superficie de cookies, CORS y certificados; el diseño actual no la expone.
- **Aplicación móvil:** sin superficie propia hoy.

## Resumen

| Amenaza | Estado |
|---|---|
| T1 Aislamiento entre tenants | ✅ |
| T2 Escalada intra-tenant | 🚧 |
| T3 Escalada a plataforma | ✅ |
| T4 Robo de tokens | 🚧 |
| T5 Fuerza bruta | 🚧 |
| T6 Inyección / validación | ✅ |
| T7 Secretos en repo/imagen | ✅ |
| T8 Path traversal | ✅ |
| T9 Exfiltración vía respaldos | ✅ |
| T10 Datos en logs | 🚧 |
| T11 Denegación de servicio | 🚧 |
| T12 Salto del mantenimiento | ✅ |

Los elementos pendientes corresponden a decisiones ya tomadas y recogidas en el [roadmap](../roadmap.md).
