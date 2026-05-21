# Guía Docente — Proyecto Aduana BI
## Para el profesor: cómo enseñar este proyecto paso a paso

---

## Estructura de la guía

- [Resumen del proyecto](#resumen)
- [Cómo usar los notebooks](#notebooks)
- [Secuencia de clases sugerida](#clases)
- [Diagrama de arquitectura](#diagrama)
- [Conceptos clave por clase](#conceptos)
- [Preguntas para los alumnos](#preguntas)
- [Errores comunes y cómo explicarlos](#errores)
- [Cómo ejecutar el proyecto completo](#ejecutar)

---

## Resumen del proyecto {#resumen}

Este proyecto construye un **Data Warehouse (DW)** con datos reales de despachos aduaneros,
utilizando Python, DuckDB y Power BI.

**Tecnologías:**
- Python 3.12 + pandas + duckdb
- DuckDB (base de datos SQL en un solo archivo)
- Power BI (visualización final)

**Flujo de datos:**
```
Excel (Bronze) → Staging (Silver) → Dimensiones + Fact Table (Gold) → Power BI
```

**Archivos del proyecto:**

| Archivo | Qué hace | Notebook |
|---------|----------|----------|
| `sql/CrearTablas.py` | Crea toda la estructura SQL vacía | `01_Crear_Estructura_DW.ipynb` |
| `etl/ETL-Cargar-Staging.py` | Lee Excel, limpia y carga staging | `02_Cargar_Staging.ipynb` |
| `etl/ETL-Dimension.py` | Genera las 12 dimensiones | `03_Cargar_Dimensiones.ipynb` |
| `etl/ETL-FACT.py` | Carga la fact table con 14 JOINs | `04_Cargar_Fact_Table.ipynb` |
| `etl/ConsAUX.py` | Valida integridad del DW | `05_Validaciones.ipynb` |
| `etl/ProcesoBase.py` | Ejecuta todo en orden | (referencia) |

---

## Cómo usar los notebooks {#notebooks}

### Requisitos previos para los alumnos

```bash
pip install duckdb pandas openpyxl
```

### Orden de ejecución

```
00_Arquitectura_y_Conceptos.ipynb   ← leer primero (sin ejecutar)
01_Crear_Estructura_DW.ipynb        ← ejecutar
02_Cargar_Staging.ipynb             ← ejecutar
03_Cargar_Dimensiones.ipynb         ← ejecutar
04_Cargar_Fact_Table.ipynb          ← ejecutar
05_Validaciones.ipynb               ← ejecutar
```

### ¿Cómo abrir los notebooks?

**Opción A — Jupyter Notebook/Lab (recomendado):**
```bash
pip install jupyterlab
jupyter lab
```
Luego navegar a la carpeta `notebooks/`.

**Opción B — VS Code:**
Instalar extensión "Jupyter" y abrir directamente los `.ipynb`.

**Opción C — Google Colab:**
Subir los notebooks. Ajustar las rutas `DB_PATH`, `XLSX_PATH`, `DEST_PATH` a rutas locales de Colab.

---

## Secuencia de clases sugerida {#clases}

### Clase 1 — Introducción y arquitectura (2 horas)
**Objetivo:** que los alumnos entiendan el problema y la solución antes de ver código.

1. Mostrar el archivo Excel original (`DatosXLSX.xlsx`) — así llegan los datos
2. Mostrar el dashboard Power BI (`Dash.pbix`) — así se ven al final
3. Preguntar: "¿Cómo pasamos de uno al otro?" → discusión
4. Explicar el concepto de ETL con un ejemplo cotidiano (ej: lavar y clasificar ropa)
5. Abrir `00_Arquitectura_y_Conceptos.ipynb` y recorrerlo célula por célula
6. Dibujar el Star Schema en la pizarra

**Tarea:** instalar Python, DuckDB, Jupyter. Leer el notebook 00.

---

### Clase 2 — Diseño del Data Warehouse (2 horas)
**Objetivo:** entender por qué se diseñan las tablas de esa manera.

1. Explicar la diferencia entre base de datos operacional vs Data Warehouse
2. Explicar Staging vs Dimensiones vs Fact Table
3. Abrir `01_Crear_Estructura_DW.ipynb`
4. Ejecutar célula por célula, discutiendo cada tabla
5. Señalar: ¿por qué PRIMARY KEY? ¿por qué UNIQUE? ¿por qué INTEGER vs VARCHAR?
6. Discutir: ¿qué pasa si ejecutamos el script dos veces? (respuesta: `DROP IF EXISTS`)

**Tarea:** ejecutar el notebook 01 y verificar que se creen las 15 tablas.

---

### Clase 3 — ETL: Extracción y Staging (2 horas)
**Objetivo:** entender cómo se extraen y limpian los datos.

1. Abrir el Excel original y mostrar el problema: columnas con espacios, fechas como texto
2. Explicar qué es un DataFrame de Pandas
3. Abrir `02_Cargar_Staging.ipynb`
4. Ejecutar y detenerse en el bloque de fechas: ¿qué pasa si `errors='coerce'`?
5. Mostrar el DataFrame antes y después del `rename()`
6. Explicar `con.register()` — el puente entre Pandas y DuckDB
7. Explicar `CAST()` — por qué se fuerzan los tipos

**Actividad práctica:** agregar una columna nueva al Excel y adaptar el rename.

---

### Clase 4 — ETL: Dimensiones (2 horas)
**Objetivo:** entender cómo se generan tablas de dimensiones desde el staging.

1. Recordar el concepto de dimensión: tabla descriptiva, valores únicos
2. Abrir `03_Cargar_Dimensiones.ipynb`
3. Ejecutar `dim_operacion` y discutir: ¿cuántas filas esperamos? ¿Por qué?
4. Explicar `ROW_NUMBER() OVER (ORDER BY ...)` — cómo se generan IDs surrogates
5. Profundizar en `dim_pais`: ¿por qué `SPLIT_PART`? Demostrar con un ejemplo
6. Profundizar en `dim_producto`: ¿por qué la clave es compuesta?
7. Explicar `dim_fecha`: atributos derivados y por qué se usa dos veces en la fact

**Pregunta de debate:** ¿Por qué no guardamos directamente el texto en la fact table?

---

### Clase 5 — ETL: Fact Table y JOINs (2 horas)
**Objetivo:** entender el JOIN masivo y la construcción de la fact table.

1. Dibujar en la pizarra el esquema: staging en el centro, dimensiones alrededor
2. Explicar LEFT JOIN vs INNER JOIN: ¿qué pasa con filas sin match?
3. Abrir `04_Cargar_Fact_Table.ipynb`
4. Ejecutar y analizar el resultado: ¿cuántas filas? ¿Son correctas?
5. Ejecutar la consulta analítica de ejemplo (FOB por operación)
6. Discutir: ¿qué ventaja tiene tener IDs en lugar de texto?

**Demostración:** mostrar que una consulta con JOIN es más rápida que buscar por texto.

---

### Clase 6 — Validación e integridad de datos (1 hora)
**Objetivo:** entender por qué validar y cómo detectar problemas.

1. Abrir `05_Validaciones.ipynb`
2. Ejecutar cada validación y explicar qué significaría si falla
3. Introducir el concepto de "clave huérfana" con un ejemplo sencillo
4. Discutir: ¿qué haríamos si encontramos 50 claves huérfanas?

---

### Clase 7 — Power BI y cierre (1 hora)
**Objetivo:** ver el resultado final y conectar todo.

1. Abrir `Dash.pbix` y mostrar los reportes
2. Mostrar cómo Power BI se conecta a DuckDB vía ODBC
3. Explicar por qué el modelo dimensional es ideal para Power BI
4. Repaso general: preguntas abiertas

---

## Diagrama de arquitectura {#diagrama}

```
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA BRONZE (Fuente)                        │
│                                                                 │
│   DatosXLSX.xlsx                LISTADO_DE_DESTINACIONES.xlsx  │
│   (despachos aduaneros)         (catálogo de códigos)          │
└──────────────────┬──────────────────────┬───────────────────────┘
                   │                      │
                   ▼  ETL-Cargar-Staging  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA SILVER (Staging)                       │
│                                                                 │
│   dw.stg_aduana (41 cols)       dw.stg_destinaciones (4 cols) │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼  ETL-Dimension
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA GOLD (Dimensiones)                     │
│                                                                 │
│  dim_operacion     dim_destinacion   dim_regimen   dim_aduana  │
│  dim_pais          dim_producto      dim_canal     dim_fecha   │
│  dim_medio_transporte  dim_unidad_medida  dim_acuerdo          │
│  dim_marca                                                      │
└──────────────────────────────────┬──────────────────────────────┘
                                   │
                                   ▼  ETL-FACT
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA GOLD (Fact Table)                      │
│                                                                 │
│   dw.fact_aduana_item                                          │
│   ├── id_fact (PK)                                             │
│   ├── despacho_cifrado + item (clave natural)                  │
│   ├── 14 FK → dimensiones                                      │
│   └── 19 métricas numéricas                                    │
└──────────────────────────────────┬──────────────────────────────┘
                                   │  ODBC
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                     VISUALIZACIÓN                               │
│   Power BI — Dash.pbix                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Conceptos clave por clase {#conceptos}

### Clase 1
| Concepto | Definición simple |
|----------|-------------------|
| ETL | Extraer, Transformar, Cargar datos |
| Data Warehouse | BD optimizada para análisis, no operaciones |
| Bronze/Silver/Gold | Capas de madurez de los datos |

### Clase 2
| Concepto | Definición simple |
|----------|-------------------|
| Schema SQL | Carpeta que agrupa tablas relacionadas |
| Clave surrogate | ID artificial que generamos nosotros (1, 2, 3...) |
| Clave natural | El ID del negocio (despacho_cifrado) |
| Staging | Tabla de paso antes de transformar |

### Clase 3
| Concepto | Definición simple |
|----------|-------------------|
| DataFrame | Tabla en memoria de Python (pandas) |
| `pd.to_datetime()` | Convierte texto a fecha real |
| `errors='coerce'` | Si falla la conversión, pone NULL en lugar de error |
| `CAST()` | Forzar tipo de dato en SQL |

### Clase 4
| Concepto | Definición simple |
|----------|-------------------|
| `SELECT DISTINCT` | Trae solo valores únicos |
| `ROW_NUMBER()` | Función de ventana que numera filas |
| `SPLIT_PART()` | Divide un texto por un separador |
| `UNION` (sin ALL) | Combina resultados eliminando duplicados |
| Clave compuesta | Unicidad definida por la combinación de varios campos |

### Clase 5
| Concepto | Definición simple |
|----------|-------------------|
| `LEFT JOIN` | Trae todo de la tabla izquierda, aunque no haya match |
| `INNER JOIN` | Solo trae filas con match en ambas tablas |
| Alias de tabla | Nombre corto para referenciar la misma tabla dos veces (po, pd) |
| `COALESCE(campo, '')` | Reemplaza NULL con un valor por defecto |

### Clase 6
| Concepto | Definición simple |
|----------|-------------------|
| Clave huérfana | FK que no tiene match en la dimensión |
| Integridad referencial | Garantía de que las FK siempre apuntan a algo válido |
| `HAVING` | Filtro sobre grupos (se usa después de `GROUP BY`) |

---

## Preguntas para los alumnos {#preguntas}

### Conceptuales
1. ¿Por qué no guardamos directamente el texto "IMPORTACION" en la fact table?
2. ¿Qué pasaría si alguien cambia el nombre de una aduana en los datos fuente?
3. ¿Por qué `dim_pais` se usa dos veces en la fact table (origen y destino)?
4. ¿Por qué `dim_fecha` también se usa dos veces?
5. ¿Qué ventaja tiene el modelo Star Schema sobre tener todo en una sola tabla?

### Técnicas
1. ¿Qué devuelve `SPLIT_PART('BRA - BRASIL', ' - ', 2)`?
2. ¿Qué diferencia hay entre `DELETE FROM tabla` y `DROP TABLE tabla`?
3. ¿Qué pasa si hay un valor en `stg_aduana.operacion` que no está en `dim_operacion`?
4. ¿Por qué se usa `COALESCE(campo, '')` en el JOIN de `dim_producto`?
5. Si el Excel tiene 500 filas y `dim_aduana` tiene 8, ¿cuántas filas debería tener la fact table?

---

## Errores comunes y cómo explicarlos {#errores}

### "Connection already closed!"
**Causa:** se llamó `con.close()` y luego se intentó usar `con` de nuevo.
**Lección:** la conexión a DuckDB es un recurso que hay que abrir y cerrar una sola vez.
**Analogía:** es como colgar el teléfono y tratar de seguir hablando.

### "Column not found"
**Causa:** el rename de columnas no coincide exactamente (espacios, acentos, mayúsculas).
**Lección:** los datos del mundo real son sucios. Siempre hay que verificar los nombres exactos.
**Solución:** imprimir `df.columns.tolist()` para ver exactamente qué llegó.

### "Duplicate key violation"
**Causa:** se insertó dos veces la misma clave primaria o unique.
**Lección:** el `DELETE FROM tabla` antes del INSERT es fundamental para idempotencia.
**Concepto:** idempotencia = ejecutar el script N veces da siempre el mismo resultado.

### Fact table con menos filas que el staging
**Causa:** algún INNER JOIN filtró filas sin match.
**Lección:** en ETL, los LEFT JOIN preservan todos los datos originales.

### Fechas NULL al 100%
**Causa:** el formato del Excel no coincide con el `format=` en `pd.to_datetime()`.
**Solución:** imprimir `df['OFICIALIZACION'].head()` para ver el formato real.

---

## Cómo ejecutar el proyecto completo {#ejecutar}

### Opción 1: Ejecutar cada script por separado (para enseñanza)

```bash
python sql/CrearTablas.py
python etl/ETL-Cargar-Staging.py
python etl/ETL-Dimension.py
python etl/ETL-FACT.py
python etl/ConsAUX.py
```

### Opción 2: Ejecutar todo de una vez (para producción)

```bash
python etl/ProcesoBase.py
```

### Verificar que todo está bien

Después de ejecutar, abrir DuckDB y correr:

```sql
SELECT table_name, (SELECT COUNT(*) FROM dw.{table_name}) AS filas
FROM information_schema.tables
WHERE table_schema = 'dw'
ORDER BY table_name;
```

### Resultados esperados

| Tabla | Filas esperadas |
|-------|----------------|
| stg_aduana | = filas del Excel |
| stg_destinaciones | = filas del catálogo |
| dim_operacion | 2 (IMPORTACION, EXPORTACION) |
| dim_fecha | cantidad de fechas únicas |
| fact_aduana_item | = stg_aduana (menos filas con clave nula) |

---

## Notas para el docente

- Los notebooks están pensados para ejecutarse **célula por célula**, con pausa entre cada una para discutir.
- Cada notebook tiene celdas de **verificación al final** — úsalas para mostrar el resultado esperado.
- El proyecto usa datos reales de aduana, lo que lo hace valioso para contextualizar a los alumnos en el ámbito profesional.
- Si los alumnos tienen problemas con las rutas de archivo, recordarles que deben ajustar `DB_PATH`, `XLSX_PATH` y `DEST_PATH` a su equipo.
- DuckDB es ideal para enseñanza porque **no requiere instalar un servidor** — toda la BD es un archivo.
