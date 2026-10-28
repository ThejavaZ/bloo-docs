# Contribuir con la documentación de Bloo

Gracias por tu interés en mejorar la documentación de Bloo. Este repositorio contiene **documentación técnica en Markdown y diagramas Mermaid**; no contiene código ejecutable de la plataforma.

## Reglas del repositorio

1. **Documentación pura.** Solo se aceptan archivos `.md`, `.mmd` (Mermaid) y, eventualmente, imágenes de apoyo. Nada de código fuente, dependencias ni artefactos de compilación.
2. **Sin información sensible.** Nada de credenciales, tokens, claves, IPs privadas, datos de usuarios reales o valores reales de variables de entorno. Usa siempre ejemplos ficticios (`empresa.test`, `user@ejemplo.com`, `token-ejemplo`).
3. **Estado explícito.** Al describir funcionalidades, indica su estado con el vocabulario del proyecto:
   - ✅ **Implementado** — existe y está verificado por la suite de pruebas.
   - 🚧 **En desarrollo** — trabajo en curso.
   - 📋 **Planeado** — diseñado pero no implementado.
4. **Documentar lo real.** Este repositorio describe el sistema tal como es (o tal como se decidió que fuera), no como nos gustaría que fuera. Las ideas futuras van en [docs/roadmap.md](docs/roadmap.md) o en un ADR con estado *Propuesto*, nunca como si ya estuvieran implementadas.

## Estructura

```text
Bloo-Docs/
├── README.md                      ← punto de entrada
├── docs/
│   ├── overview.md                ← qué es Bloo y estado por módulo
│   ├── requirements.md            ← requisitos funcionales/no funcionales
│   ├── roadmap.md                 ← backlog y dirección
│   ├── architecture/
│   │   ├── system-design.md
│   │   ├── tenancy-model.md
│   │   ├── data-model.md
│   │   ├── authentication-and-authorization.md
│   │   ├── error-handling.md
│   │   └── decisions/             ← ADRs
│   ├── api/                       ← convenciones del contrato HTTP
│   ├── security/                  ← aislamiento y modelo de amenazas
│   └── operations/                ← logs y configuración
└── diagrams/                      ← fuentes Mermaid
```

## Estilo de escritura

- **Idioma:** español. Los nombres técnicos en inglés (`middleware`, `endpoint`, `tenant`) se conservan como tales.
- **Tercera persona o voz neutra**; evitar marketing. Este es un documento técnico, no un folleto.
- **Ejemplos concretos:** prefiere un ejemplo JSON corto a tres párrafos de descripción.
- **Enlaces relativos** entre documentos (`[modelo de tenancy](docs/architecture/tenancy-model.md)`), nunca rutas absolutas del sistema de archivos.
- **Tablas** para comparaciones y listas de estados; **Mermaid** para diagramas (GitHub los renderiza dentro de los `.md`).
- Títulos en `Title Case` solo para nombres propios; encabezados en minúsculas normales.
- Cada documento empieza con una línea de estado si aplica: `> Estado: ✅ Implementado`.

## ADR (Architecture Decision Records)

Las decisiones arquitectónicas se documentan en [`docs/architecture/decisions/`](docs/architecture/decisions/) con numeración secuencial y nombre en `kebab-case`:

```text
NNNN-titulo-corto-de-la-decision.md
```

Plantilla:

```markdown
# NNNN. Título de la decisión

- **Estado:** Aceptada | Propuesta | Supersedida por NNNN | Obsoleta
- **Fecha:** YYYY-MM-DD
- **Contexto:** qué problema o restricción obligó a decidir.

## Opciones evaluadas

| Opción | Ventajas | Desventajas |
|---|---|---|

## Decisión

Qué se eligió y por qué, con los criterios concretos que inclinaron la balanza.

## Consecuencias

Qué se gana, qué se pierde y qué restricciones impone la decisión en el futuro.
```

Un ADR se escribe **después** de tomar la decisión y se actualiza si cambia su estado (por ejemplo, al ser supersedida). No se edita retroactivamente el contenido del contexto ni de la decisión.

## Cómo proponer cambios

1. Abre un *issue* describiendo qué documento está desactualizado o qué concepto falta por documentar.
2. Para cambios pequeños (erratas, enlaces, claridades), un PR directo es bienvenido.
3. Para reestructuración de carpetas o cambios de alcance, discute primero en un *issue*.
4. En el PR, explica **qué documento cambia y por qué**. Si el cambio refleja un cambio de código, menciónalo.

## Licencia de las contribuciones

Al contribuir aceptas que tu aporte se publica bajo la misma licencia del repositorio: [CC BY 4.0](LICENSE), con atribución a ti y al proyecto.
