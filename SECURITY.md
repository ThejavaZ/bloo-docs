# Seguridad

## Alcance de este repositorio

`bloo-docs` contiene **únicamente documentación técnica** de la plataforma Bloo: arquitectura, decisiones, convenciones de API y modelo de amenazas. No contiene código ejecutable, credenciales ni datos de usuarios.

Un reporte de seguridad en este repositorio puede ser:

1. **Información sensible publicada por error** en la documentación (credenciales, datos personales, detalles operativos que deberían ser privados).
2. **Una debilidad del diseño descrito** que convenga corregir en el sistema (por ejemplo, un hueco en la estrategia de aislamiento de tenants documentada en [`docs/security/tenant-isolation.md`](docs/security/tenant-isolation.md)).

Los fallos del software en sí se reportan en el repositorio de implementación correspondiente (`erp-api` o `erp-client`).

## Cómo reportar

- **Preferido:** reporte privado de GitHub → pestaña *Security* → *Report a vulnerability*.
- **Alternativa:** abre un issue con la plantilla *Reporte de seguridad* **sin detalles de explotación** y deja constancia de que puedes ser contactado en privado.

Por favor, no divulgues públicamente una vulnerabilidad antes de que pueda atenderse.

## Qué esperar

- Acuse de recibo tan pronto como sea posible.
- Evaluación del impacto y comunicación de los próximos pasos.
- Corrección y, si aplica, actualización de la documentación afectada.
- Atribución en el changelog si lo deseas (con tu permiso expreso).
