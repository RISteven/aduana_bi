# ⚡ Quick Start — DWH en 20 minutos

**Si no tienes mucho tiempo y quieres entender el flujo rápido...**

---

## El problema en 30 segundos

Tienes un Excel gigante con datos de aduanas. Quieres analizarlo en Power BI pero está:
- ❌ Lleno de espacios y caracteres raros
- ❌ Datos repetidos (BRASIL aparece 10,000 veces)
- ❌ Fechas como texto, no como fechas reales
- ❌ Muy lento de procesar

## La solución en 30 segundos

Construimos un **Data Warehouse**: una base de datos especial para análisis donde:
- ✅ Todo está limpio y normalizado
- ✅ No hay repeticiones (BRASIL aparece 1 sola vez)
- ✅ Las fechas son verdaderas fechas
- ✅ Es rápido y eficiente

---

## Las 4 fases de construcción

### 🏗️ Fase 1: Arquitectura (15 minutos)

**Ejecuta:** `notebooks/01_Crear_Estructura_DW.ipynb`

```python
# Esto crea 15 tablas vacías:
# - 1 tabla de staging (zona de paso)
# - 12 tablas de dimensiones (catálogos)
# - 1 tabla de hechos (datos principales)
# - 1 tabla de auditoría (historial)
```

**Verifica:**
```python
con.query('SELECT COUNT(*) FROM sqlite_master WHERE type="table"')
# Deberías ver: 15 tablas
```

---

### 🧹 Fase 2: Limpieza (20 minutos)

**Ejecuta:** `notebooks/02_Cargar_Staging.ipynb`

```python
# Esto:
# 1. Lee el Excel
# 2. Quita espacios de nombres de columnas
# 3. Convierte fechas de texto a fechas reales
# 4. Limpia espacios en blanco
# 5. Guarda todo en stg_aduana (41,342 filas)
```

**Verifica:**
```python
con.query('SELECT COUNT(*) FROM stg_aduana')
# Deberías ver: ~41,342
```

---

### 📚 Fase 3: Dimensiones (15 minutos)

**Ejecuta:** `notebooks/03_Cargar_Dimensiones.ipynb`

```python
# Esto crea catálogos sin repetición:
# dim_operacion: 2 tipos (IMPORTACION, EXPORTACION)
# dim_pais: ~50 países
# dim_aduana: ~8 aduanas
# dim_producto: ~500 productos
# ... más dimensiones ...
```

**Verifica:**
```python
con.query('SELECT COUNT(*) FROM dim_pais')
# Deberías ver: ~50 (no 10,000 repeticiones)
```

---

### 🔗 Fase 4: Tabla de hechos (20 minutos)

**Ejecuta:** `notebooks/04_Cargar_Fact_Table.ipynb`

```python
# Esto hace 14 JOINs gigantescos:
# Toma stg_aduana y busca el ID de cada dimensión
# Resultado: fact_aduana_item con referencias numéricas
```

**Verifica:**
```python
con.query('SELECT COUNT(*) FROM fact_aduana_item')
# Deberías ver: ~41,342 (casi igual a staging, porque usamos LEFT JOIN)
```

---

## La arquitectura visual

```
EXCEL (desordenado)
    ↓
STAGING (limpio pero con repeticiones)
    ↓ 
DIMENSIONES (catálogos sin repetir)
    ↓ JOINS
FACT TABLE (hechos conectados a catálogos)
    ↓ ODBC
POWER BI (reportes rápidos)
```

---

## Validaciones rápidas

Ejecuta: `notebooks/05_Validaciones.ipynb`

```python
# Verifica:
# ✓ No hay claves huérfanas
# ✓ No hay duplicados
# ✓ No hay valores negativos absurdos
# ✓ Las fechas tienen sentido
```

Si todo dice "✓ PASADO", estás listo para Power BI.

---

## Conectar a Power BI (5 minutos)

**Opción A: ODBC (recomendado)**
```bash
pip install duckdb-odbc
# En Power BI: File → Get Data → ODBC
# Selecciona DuckDB, apunta a: C:\...\aduana.duckdb
```

**Opción B: CSV**
```python
# Si ODBC no funciona, exporta a CSV:
con.query('SELECT * FROM fact_aduana_item').to_df().to_csv('fact.csv')
# Luego importa en Power BI desde CSV
```

---

## Estructura de carpetas

```
aduana_bi/
├── db/
│   └── aduana.duckdb          ← tu Data Warehouse
├── data_lake/
│   ├── bronze/
│   │   └── DatosCSV.csv       ← datos originales (desordenados)
│   ├── silver/
│   │   └── (vacío, intermediario)
│   └── gold/
│       └── (vacío, resultado final)
├── etl/
│   ├── CrearTablas.py
│   ├── ETL-Cargar-Staging.py
│   ├── ETL-Dimension.py
│   └── ETL-FACT.py
└── notebooks/
    ├── 01_Crear_Estructura_DW.ipynb
    ├── 02_Cargar_Staging.ipynb
    ├── 03_Cargar_Dimensiones.ipynb
    ├── 04_Cargar_Fact_Table.ipynb
    └── 05_Validaciones.ipynb
```

---

## Flujo de ejecución

```
1. EJECUTA notebooks/01_*.ipynb    → Crea estructura vacía
2. EJECUTA notebooks/02_*.ipynb    → Carga y limpia datos
3. EJECUTA notebooks/03_*.ipynb    → Crea dimensiones
4. EJECUTA notebooks/04_*.ipynb    → Crea tabla de hechos
5. EJECUTA notebooks/05_*.ipynb    → Valida todo
6. ABRE Power BI                   → Conecta y visualiza
```

**Tiempo total:** ~2-3 horas (según tu experiencia)

---

## Diccionario de datos (lo mínimo que necesitas saber)

| Tabla | Significado |
|-------|------------|
| `stg_aduana` | Datos originales limpios (staging) |
| `dim_operacion` | Tipos: IMPORTACION, EXPORTACION |
| `dim_pais` | Lista de países (origen y destino) |
| `dim_producto` | Categorías de productos (HS Code) |
| `dim_fecha` | Fechas con atributos (año, mes, trimestre) |
| `fact_aduana_item` | Hechos: cada línea es un ítem de un despacho |

---

## Ejemplos de análisis en Power BI

Una vez conectado, puedes crear:

1. **Total FOB por operación** (¿cuánto se importó vs exportó?)
2. **Top 10 países** (¿con quién comerciamos más?)
3. **Productos más importados** (¿qué traemos del exterior?)
4. **Tendencia mensual** (¿va creciendo?)
5. **Análisis por aduana** (¿dónde entra más mercancía?)

---

## Si algo falla...

| Error | Solución |
|-------|----------|
| "Column not found" | El Excel tiene nombres diferentes. Revisa el notebook 02. |
| "Connection closed" | No hagas `con.close()` hasta el final. |
| "File not found" | Verifica que `data_lake/bronze/DatosCSV.csv` existe. |
| "FK huérfana" | Hay datos que no coinciden con la dimensión. Revisa el validate. |
| ODBC no funciona | Usa la opción B (CSV). |

---

## Tiempo estimado por paso

| Paso | Tiempo | Acción |
|------|--------|--------|
| Instalar | 5 min | `pip install duckdb pandas openpyxl jupyterlab` |
| Entender | 10 min | Lee la sección "Conceptos" arriba |
| Arquitectura | 15 min | Ejecuta notebook 01 |
| Limpieza | 20 min | Ejecuta notebook 02 |
| Dimensiones | 15 min | Ejecuta notebook 03 |
| Hechos | 20 min | Ejecuta notebook 04 |
| Validación | 10 min | Ejecuta notebook 05 |
| Power BI | 30 min | Conecta y crea reportes |
| **TOTAL** | **~2:15 h** | ✅ DWH completo |

---

## Comandos útiles (Python)

```python
import duckdb

# Conectar
con = duckdb.connect('db/aduana.duckdb')

# Ver cuántas filas hay en cada tabla
con.query('SELECT COUNT(*) FROM stg_aduana').show()
con.query('SELECT COUNT(*) FROM fact_aduana_item').show()

# Ver las primeras 5 filas
con.query('SELECT * FROM dim_pais LIMIT 5').show()

# Contar dimensiones
con.query('SELECT COUNT(*) FROM dim_operacion').show()
con.query('SELECT COUNT(*) FROM dim_pais').show()

# Análisis rápido
con.query('''
SELECT 
    operacion,
    COUNT(*) as total,
    SUM(fob) as total_fob
FROM fact_aduana_item
GROUP BY operacion
''').show()
```

---

**Para más detalles, lee:** `PASO_A_PASO_DWH.md`

