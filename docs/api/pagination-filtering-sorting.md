# Paginación, filtrado y ordenamiento

> Estado: ✅ Paginación y filtrado implementados · 📋 Ordenamiento pendiente.

## Paginación

### Forma

Los listados se pagan con el paginador nativo de Laravel y se envuelven en `meta` con **cuatro claves fijas**:

```json
{
  "success": true,
  "data": [ … ],
  "meta": {
    "current_page": 1,
    "last_page": 3,
    "per_page": 15,
    "total": 42
  }
}
```

No se envía el bloque `links` completo de Laravel: el cliente conoce la página actual y el total, y calcula el resto.

### Parámetros

| Parámetro | Default | Notas |
|---|---|---|
| `page` | `1` | Entero positivo |
| `per_page` | `15` | Varía por recurso (por ejemplo, `/api/companies` usa 10). El panel Landlord limita `per_page` a un rango de 1–100 en su listado de tenants |

### Ejemplo

```http
GET /api/clients?page=2&per_page=15
Authorization: Bearer <token>
```

## Búsqueda

El parámetro `search` aplica un `LIKE` sobre los campos de texto relevantes de cada recurso:

| Recurso | Campos buscados |
|---|---|
| `/api/clients` | nombre, RFC, nombre de empresa |
| `/api/products` | nombre, SKU |
| Otros CRUD | nombre u equivalente |

```http
GET /api/clients?search=lopez
```

En el frontend, la búsqueda se envía con **debounce de 400 ms** desde la barra de filtros, para no generar una petición por tecla.

## Filtros

| Parámetro | Recursos | Vocabulario |
|---|---|---|
| `status` | `/api/clients` | `Activo`, `Inactivo`, `Prospecto` |
| `status` | `/api/invoices` | `draft`, `issued`, `paid`, `overdue`, `cancelled` |
| `status` | `/api/expenses` | `Pendiente`, `Pagado` |
| `category` | `/api/expenses` | Categorías de gasto (Operación, Nómina, Servicios, Impuestos, Otros) |

> El vocabulario de `status` **no es uniforme** entre recursos: los módulos más antiguos usan estados en español y los nuevos, en inglés. Cambiarlo rompería clientes existentes; está anotado como deuda de consistencia en el [roadmap](../roadmap.md).

## Ordenamiento

**No existe una convención de ordenamiento.** Los listados devuelven el orden por defecto de la base de datos (típicamente por llave primaria ascendente). Esto implica que:

- No se puede pedir explícitamente "los más recientes primero".
- No hay garantía documentada del orden entre páginas.

### Convención propuesta (📋 pendiente de implementación)

```http
GET /api/invoices?sort=issued_at:desc
```

- Un solo campo por petición en esta fase (orden múltiple en el futuro).
- Formato `campo:direccion` con `asc` por defecto si se omite la dirección.
- Solo campos **blancos** por recurso (evita ordenar por columnas internas o sensibles).
- Inválido → 422 con mensaje claro, nunca un orden silencioso distinto al pedido.

Al implementarse, esta sección pasará a ✅ y el ADR correspondiente quedará registrado en [../architecture/decisions/](../architecture/decisions/).

## Búsqueda en el Landlord

Los endpoints del panel administrativo añaden filtros propios:

- `/api/admin/audit-logs`: `action`, `target_company_id`, `from`, `to`.
- `/api/admin/payments`: filtro por estado de pago.
- `/api/admin/tenants`: búsqueda y `per_page` acotado a 1–100.

## Recomendaciones para nuevos endpoints

1. Usa el paginador nativo y devuelve `meta` con las cuatro claves; no inventes otra forma.
2. Documenta en `docs/API.md` qué campos cubre `search` y qué valores acepta `status`.
3. Si el recurso admite fechas, expón filtros `from`/`to` con el mismo criterio que auditoría.
4. Cuando se implemente `sort`, aplícalo también a los endpoints nuevos desde el día uno.
