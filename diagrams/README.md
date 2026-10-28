# Diagramas

Fuentes Mermaid de los diagramas de la arquitectura de Bloo. GitHub renderiza los bloques ` ```mermaid ` incluidos en los documentos de `docs/`; estos archivos `.mmd` son las **fuentes independientes**, útiles para editar, versionar y regenerar imágenes.

| Archivo | Describe | Documento asociado |
|---|---|---|
| [system-context.mmd](system-context.mmd) | Sistema en su entorno: actores, componentes y fronteras | [system-design.md](../docs/architecture/system-design.md) |
| [tenancy-model.mmd](tenancy-model.mmd) | Identificación del tenant y capas de aislamiento | [tenancy-model.md](../docs/architecture/tenancy-model.md) |
| [request-lifecycle.mmd](request-lifecycle.mmd) | Recorrido de una petición de negocio end-to-end | [system-design.md](../docs/architecture/system-design.md) |

## Renderizar

- **En línea:** los `.md` de este repositorio ya los muestran en GitHub.
- **Como imagen:** [Mermaid Live Editor](https://mermaid.live) o CLI:

```bash
npx @mermaid-js/mermaid-cli -i diagrams/system-context.mmd -o diagrams/system-context.svg
```

## Convenciones

- Los diagramas describen **el estado actual**, no el deseado.
- Nada de credenciales, hosts reales ni datos de usuarios: solo nombres de componentes y flujos.
- Si un diagrama queda desactualizado respecto a un documento, prevalece el documento y se corrige el diagrama en el mismo PR.
