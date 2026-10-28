# Requisitos

> Estado: ✅ Implementados salvo indicación contraria. Este documento separa lo que **ya funciona y está probado** de lo que está **diseñado pero pendiente**.

## Requisitos funcionales

### RF-1 Gestión de empresas (tenants)

| ID | Requisito | Estado |
|---|---|---|
| RF-1.1 | El operador puede crear, editar y dar de baja empresas desde el Panel Landlord | ✅ |
| RF-1.2 | Cada empresa tiene plan, fechas de suscripción y periodo de prueba | ✅ |
| RF-1.3 | Una empresa puede ponerse en **modo mantenimiento**: toda la API de negocio responde 503, excepto autenticación y el Panel Landlord | ✅ |
| RF-1.4 | El slug de la empresa es único en la plataforma | ✅ |
| RF-1.5 | Resolución de tenant por dominio propio (`domain`) | 📋 El campo existe en el modelo; la resolución por HTTP aún no está implementada |

### RF-2 Identidad y acceso

| ID | Requisito | Estado |
|---|---|---|
| RF-2.1 | Registro, login y cierre de sesión con token Bearer | ✅ |
| RF-2.2 | Recuperación de contraseña por correo | ✅ (el envío usa el mailer configurado; en desarrollo escribe a log) |
| RF-2.3 | Cambio de contraseña revoca los demás tokens del usuario | ✅ |
| RF-2.4 | El usuario puede revocar todos sus tokens activos | ✅ |
| RF-2.5 | El correo es único **dentro** de una empresa, no en la plataforma | ✅ |
| RF-2.6 | Segundo factor de autenticación (2FA) | 📋 Columnas reservadas en `users`; sin flujos implementados |

### RF-3 Autorización

| ID | Requisito | Estado |
|---|---|---|
| RF-3.1 | 5 roles por empresa: `super_admin`, `admin`, `manager`, `employee`, `guest` | ✅ |
| RF-3.2 | ~107 permisos granulares (`view_clients`, `create_invoices`…) agrupados en ~18 módulos | ✅ |
| RF-3.3 | Los roles viven en el contexto de su empresa (`team_id = company_id`); un usuario no puede ver heredar roles ajenos | ✅ |
| RF-3.4 | El sidebar del frontend oculta elementos sin permiso del usuario | ✅ |
| RF-3.5 | Verificación de permisos en **todas** las rutas de negocio | 🚧 Hoy el refuerzo por ruta (`role_or_permission`) se aplica en usuarios, categorías, marcas, unidades y almacenes; el resto depende del aislamiento de tenant |

### RF-4 Catálogos e inventario

| ID | Requisito | Estado |
|---|---|---|
| RF-4.1 | Productos con SKU único por empresa, código de barras, precios de costo y venta, tasa de impuesto y atributos JSON | ✅ |
| RF-4.2 | Marcas, categorías y unidades como catálogos CRUD por empresa | ✅ |
| RF-4.3 | Almacenes con stock por producto | ✅ |
| RF-4.4 | Imágenes de producto | ✅ |
| RF-4.5 | Carga masiva de productos (`POST /products/bulk`) | ✅ |

### RF-5 Ventas

| ID | Requisito | Estado |
|---|---|---|
| RF-5.1 | Clientes con tipo (persona física / empresa / gobierno), estado (activo / inactivo / prospecto) y RFC único por empresa | ✅ |
| RF-5.2 | Facturas con folio automático `INV-AAAA-NNNN` único por empresa | ✅ |
| RF-5.3 | Ciclo de vida de factura: `draft → issued → paid → overdue → cancelled` | ✅ |
| RF-5.4 | La factura conserva una instantánea del nombre del cliente (`client_name`) aunque el cliente cambie o se dé de baja | ✅ |
| RF-5.5 | Notas de crédito, envío por correo y timbrado fiscal | 📋 Fuera del alcance actual |

### RF-6 Finanzas

| ID | Requisito | Estado |
|---|---|---|
| RF-6.1 | Gastos con categoría, método de pago y estado (pendiente / pagado) | ✅ |
| RF-6.2 | Impuestos por empresa (código único por tenant, tipo IVA/ISR/IEPS/Retención) | ✅ |
| RF-6.3 | Cuentas bancarias y movimientos de ingreso/egreso | ✅ |
| RF-6.4 | Presupuestos y flujo de caja | 📋 Solo permisos y plantillas |

### RF-7 Trabajo

| ID | Requisito | Estado |
|---|---|---|
| RF-7.1 | Tablero Kanban por empresa: tableros, columnas y tarjetas con orden y asignación | ✅ |
| RF-7.2 | Reordenamiento de tarjetas (`PATCH /kanban/cards/reorder`) | ✅ |
| RF-7.3 | RRHH, proyectos, CRM y marketing | 📋 Sin backend |

### RF-8 Plataforma (Landlord)

| ID | Requisito | Estado |
|---|---|---|
| RF-8.1 | Dashboard global con MRR, crecimiento y alertas | ✅ |
| RF-8.2 | Impersonación de tenant con token temporal de 1 hora, auditada | ✅ |
| RF-8.3 | Revocación masiva de tokens de un tenant | ✅ |
| RF-8.4 | Planes con límites de usuarios y productos; al eliminar un plan se anula la referencia en las empresas | ✅ |
| RF-8.5 | Historial de pagos con estados (pagado / pendiente / fallido) y renovación manual | ✅ |
| RF-8.6 | Respaldo por tenant (volcado SQL comprimido) con descarga protegida | ✅ |
| RF-8.7 | Anuncios globales activables con ventana de vigencia | ✅ |
| RF-8.8 | Registro de auditoría de acciones del landlord con filtros | ✅ |
| RF-8.9 | Salud del sistema (base de datos, disco, tiempo de respuesta) y visor de logs | ✅ |
| RF-8.10 | Cobro automático de suscripciones | 📋 El campo de pago se registra manualmente |

## Requisitos no funcionales

### RNF-1 Aislamiento multi-tenant

| ID | Requisito | Estado |
|---|---|---|
| RNF-1.1 | Ningún usuario puede leer o modificar datos de otra empresa; la violación responde 403 | ✅ Verificado por pruebas en clientes, facturas, gastos, impuestos, productos, cuentas bancarias y usuarios |
| RNF-1.2 | Los listados solo contienen registros de la empresa del usuario | ✅ Verificado por pruebas |
| RNF-1.3 | El respaldo de un tenant contiene únicamente sus datos | ✅ Verificado por prueba |
| RNF-1.4 | El superadmin del Panel Landlord opera sin filtro de empresa | ✅ Verificado por prueba |

### RNF-2 Seguridad

| ID | Requisito | Estado |
|---|---|---|
| RNF-2.1 | Autenticación por token Bearer; sin tokens en URL ni cookies para la API | ✅ |
| RNF-2.2 | Contraseñas con bcrypt; nunca se almacenan en texto plano | ✅ |
| RNF-2.3 | Los endpoints de Landlord exigen el rol `super_admin` | ✅ Verificado por pruebas |
| RNF-2.4 | La descarga de respaldos valida el nombre de archivo (sin traversal) | ✅ |
| RNF-2.5 | CORS restringido a los orígenes del frontend | ✅ (por entorno) |
| RNF-2.6 | Rate limiting en autenticación | 📋 No implementado |
| RNF-2.7 | Expiración de tokens | 📋 Los tokens no expiran por defecto; solo el de impersonación tiene TTL de 1 hora |

### RNF-3 Confiabilidad y datos

| ID | Requisito | Estado |
|---|---|---|
| RNF-3.1 | Integridad referencial: cada registro operativo pertenece a una empresa con FK en cascada | ✅ |
| RNF-3.2 | Úndices únicos compuestos por tenant (SKU, RFC, folio de factura, código de impuesto) | ✅ |
| RNF-3.3 | Borrado lógico (soft deletes) en entidades con historial sensible (usuarios, empresas, productos, catálogos) | ✅ |
| RNF-3.4 | Auditoría de acciones críticas del landlord (quién, qué, a qué empresa, IP) | ✅ |
| RNF-3.5 | Registro de intentos de login (fecha, IP, éxito) | ✅ Tabla `user_logins` |
| RNF-3.6 | Tareas en segundo plano (colas) | 🚧 Infraestructura lista (tablas y driver `database`); sin jobs implementados aún |

### RNF-4 Portabilidad y despliegue

| ID | Requisito | Estado |
|---|---|---|
| RNF-4.1 | El backend arranca con SQLite sin configuración; es compatible con MySQL y PostgreSQL vía entorno | ✅ |
| RNF-4.2 | Despliegue en contenedores sin instalar PHP ni Node en el host | ✅ Docker dev y prod |
| RNF-4.3 | Imagen de producción sin dependencias de desarrollo, con OPcache | ✅ |
| RNF-4.4 | Claves y configuración sensible inyectadas por entorno, no embebidas en la imagen | ✅ |
| RNF-4.5 | Suite de pruebas automatable en integración (base en memoria) | ✅ 77 pruebas / 345 assertions |

### RNF-5 Rendimiento

| ID | Requisito | Estado |
|---|---|---|
| RNF-5.1 | Listados paginados (15 por página por defecto) con índice por `company_id` | ✅ |
| RNF-5.2 | Búsqueda con debounce en el cliente (400 ms) para no saturar la API | ✅ |
| RNF-5.3 | Caché y sesiones en base de datos por defecto, migrables a Redis | 🚧 Configurado, sin carga medida |
| RNF-5.4 | Métricas de rendimiento y presupuesto de tiempos | 📋 Sin definir |

## Fuera de alcance (por ahora)

- Timbrado fiscal (SAT) y generación de CFDI.
- App móvil nativa.
- Multi-idioma completo (el modelo soporta `language` por usuario; la interfaz está en español).
- Facturación automática de suscripciones con pasarela de pago.
- SLA de disponibilidad medido.
