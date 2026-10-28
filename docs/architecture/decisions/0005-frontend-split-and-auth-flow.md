# 0005. Frontend en repositorio separado y token de sesión en `localStorage`

- **Estado:** ✅ Aceptada
- **Fecha:** 2026-08
- **Contexto:** La aplicación ERP necesita interfaz web. Hay que elegir dónde vive el frontend, con qué tecnología y cómo manejar el token de autenticación entre el navegador y la API, considerando que el backend es una API JSON y el frontend corre en otro origen durante el desarrollo.

## Opciones evaluadas

### Dónde vive el frontend

| Opción | Ventajas | Desventajas |
|---|---|---|
| **Repositorio separado desplegable de forma independiente** (elegido) | Ciclos de vida independientes (deploy del frontend sin tocar la API); equipos y ramas separados; el backend sigue siendo una API pura | Dos despliegues que coordinar; la URL de la API debe inyectarse en compilación |
| **SPA embebida en el backend (como el Panel Landlord)** | Un solo despliegue | Compilaciones acopladas; el frontend arrastra el ciclo de release del backend |
| **Next.js con Server Components contra la API** | SEO y primer pintado rápido | Irrelevante para una app autenticada tras login; añade complejidad de renderizado en servidor |

### Tecnología del frontend

Next.js 16 (App Router) con React 19, TypeScript estricto, Tailwind CSS v4 y Axios. Se eligió por consistencia con el ecosistema TypeScript y por el ecosistema de componentes disponible.

### Almacenamiento del token

| Opción | Ventajas | Desventajas |
|---|---|---|
| **`localStorage` + header Authorization** (elegido) | Simple; sin cookies ni CSRF; el interceptor de Axios lo maneja en un solo lugar | Accesible por JavaScript (riesgo de XSS); no viaja automáticamente |
| **Cookies `HttpOnly` (Sanctum stateful)** | Inmune a robo por XSS | Requiere CSRF, configuración de dominios stateful y sincronía de sesión; complejidad innecesaria para una API que ya es token-based |
| **Memory + refresh tokens** | Menor ventana de exposición | Requiere flujo de refresh completo (endpoint, rotación, persistencia) que no formaba parte del MVP |

## Decisión

1. **Frontend en su propio repositorio**, desplegable de forma independiente (imagen standalone de ~280 MB), apuntando a la API mediante la variable `NEXT_PUBLIC_API_URL` **inyectada al compilar**.
2. **Token en `localStorage`** (clave `paterno_erp_token`), inyectado por interceptor de Axios; la sesión se valida contra `GET /api/auth/user` al cargar la app (`AuthContext`).
3. **Interceptors centralizados** para el manejo transversal de 401 (sesión expirada → `/login`) y 403 (acceso denegado → `/forbidden`), con normalización de errores a una forma única.

## Consecuencias

- ✅ El frontend se despliega y prueba sin tocar la API; la API sigue siendo un contrato estable y consumible por terceros.
- ✅ Un solo punto de gestión del token: cambiarlo de `localStorage` a cookies implicaría tocar el interceptor y el `AuthContext`, nada más.
- ✅ Los manejos globales de error viven en un lugar; los servicios de recursos son simples y tipados.
- ⚠️ `localStorage` es vulnerable a XSS: obliga a mantener la plantilla del frontend libre de inyección de HTML (React lo cumple por defecto) y a revisar dependencias.
- ⚠️ El token no expira por defecto: la mitigación operativa es la revocación manual (`/auth/revoke-tokens`, cambio de contraseña, revocación por tenant desde el Landlord). La expiración está en el [roadmap](../../roadmap.md).
- ⚠️ La URL de la API fijada en compilación obliga a reconstruir la imagen ante cada cambio de entorno.
