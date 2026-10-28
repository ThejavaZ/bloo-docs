# Configuración y despliegue

> Estado: ✅ Implementado. Todo lo configurable vive en variables de entorno; ninguna lleva valores sensibles dentro de la imagen.

## Principio

**Cero configuración por defecto, todo sobreescribible por entorno.** El backend arranca con SQLite y logs a archivo sin tocar nada; producción inyecta sus valores por variables.

> Esta documentación lista **nombres** de variables, jamás valores reales. Ver [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Variables de entorno

### Aplicación

| Variable | Rol | Notas |
|---|---|---|
| `APP_NAME`, `APP_ENV`, `APP_URL` | Identidad del despliegue | `APP_ENV=production` en prod |
| `APP_KEY` | Clave maestra de cifrado | **Nunca** embebida en la imagen; se inyecta por entorno |
| `APP_DEBUG` | Detalle de errores | `false` en producción (evita filtrar trazas) |
| `APP_LOCALE`, `APP_FALLBACK_LOCALE` | Idioma | Español como base |
| `APP_MAINTENANCE_DRIVER` | Mantenimiento global de Laravel | `file` por defecto (independiente del modo mantenimiento por tenant) |

### Base de datos

| Variable | Rol |
|---|---|
| `DB_CONNECTION` | Motor: `sqlite` por defecto; compatible con `mysql` y `pgsql` |
| `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD` | Conexión (ignorados en SQLite) |

### Sesiones, caché y colas

| Variable | Default | Notas |
|---|---|---|
| `SESSION_DRIVER` | `database` | |
| `CACHE_STORE` | `database` | Redis disponible vía entorno |
| `QUEUE_CONNECTION` | `database` | La infraestructura está lista; aún no hay jobs encolados |
| `BROADCAST_CONNECTION` | `log` | Sin tiempo real implementado |

### Correo

| Variable | Rol |
|---|---|
| `MAIL_MAILER` | `log` por defecto (escribe los correos al archivo de log en desarrollo) |
| `MAIL_HOST`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` | Servidor SMTP real |
| `MAIL_FROM_ADDRESS`, `MAIL_FROM_NAME` | Remitente |

### Almacenamiento y logs

| Variable | Default |
|---|---|
| `FILESYSTEM_DISK` | `local` |
| `LOG_CHANNEL` | `stack` (en producción Docker: salida a `stderr`) |
| `LOG_LEVEL` | `warning` por defecto |

### Frontend (`erp-client`)

| Variable | Rol |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL base de la API; **se inyecta al compilar** la imagen de producción |

## Despliegue en desarrollo

```bash
# Backend
cd erp && composer install && cp .env.example .env
php artisan key:generate
touch database/database.sqlite
php artisan migrate --seed
php artisan serve            # → http://localhost:8000

# O con Docker (no requiere PHP ni Node en el host)
docker compose up --build

# Frontend
cd bloo && npm install
npm run dev                  # → http://localhost:3000
```

El código se monta como volumen: los cambios se reflejan al instante.

## Despliegue de producción

### Backend — imagen multi-etapa

```bash
export APP_KEY=<clave-generada-fuera-del-repo>
docker compose -f docker-compose.prod.yml up -d --build
```

Características de la imagen:

- Compila el Panel Landlord con Vite e instala Composer **sin dependencias de desarrollo**.
- OPcache activo; Apache como servidor.
- `APP_KEY` y `MIGRATE_ON_START=true|false` (migrar al arrancar) se inyectan por entorno.
- Los datos (SQLite + `storage/`) persisten en un volumen; `down -v` los elimina.

### Frontend — imagen standalone

- Construcción multi-etapa, imagen autónoma de ~280 MB, corriendo como usuario no root.
- La URL de la API se fija **en el momento de compilar**; cambiar de entorno implica reconstruir.

## CORS

Los orígenes permitidos se configuran por entorno y quedan restringidos a los dominios del frontend en desarrollo (`localhost` y equivalentes locales). Para producción, la lista debe ajustarse al dominio real del cliente.

`supports_credentials` está activo; la autenticación, sin embargo, es por header Bearer, no por cookies.

## Checklist antes de publicar cambios

1. **Revisar el historial de Git** del repositorio por si un archivo antiguo arrastra un `.env` o una clave.
2. Confirmar que `.env.example` refleje las variables nuevas **con valores placeholders**, nunca reales.
3. Verificar que `APP_DEBUG=false` en producción.
4. Confirmar que la imagen no contiene `.env` ni `vendor/` ni `node_modules/` de desarrollo.
5. Si cambia el esquema: migración probada contra una copia de datos reales antes de producción.
