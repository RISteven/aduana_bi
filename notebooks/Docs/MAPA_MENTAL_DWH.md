# 🗺️ Mapa Mental — DWH en una página

**Entender todo el proyecto en una sola página**

---

## El viaje de los datos (izquierda a derecha)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  EXCEL              STAGING              DIMENSIONES          FACT TABLE    │
│  CAÓTICO            LIMPIO               ORGANIZADAS          CONECTADA     │
│                                                                             │
│  ❌ Espacios        ✓ Sin espacios      ✓ Catálogos          ✓ IDs         │
│  ❌ Fechas texto    ✓ Fechas reales     ✓ Sin repetir        ✓ Relaciones  │
│  ❌ Repetido        ✓ Limpio            ✓ Normalizadas       ✓ Métricas    │
│                     ✓ 41K filas         ✓ 12 tablas          ✓ 41K filas   │
│                                                                             │
│  Excel              Notebook 02         Notebook 03          Notebook 04   │
│  original        ──────────────┐     ──────────────┐     ──────────────    │
│                                │                  │                       │
│                          stg_aduana          dim_*             fact_*      │
│                          (staging)           (12x)             (1)         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Las 5 fases en 1 minuto

| # | Fase | Entrada | Salida | Tiempo | Notebook |
|---|------|---------|--------|--------|----------|
| 1 | 🏗️ Estructura | Nada | 15 tablas vacías | 15 min | 01 |
| 2 | 🧹 Limpieza | Excel | stg_aduana limpio | 20 min | 02 |
| 3 | 📚 Dimensiones | stg_aduana | 12 catálogos | 15 min | 03 |
| 4 | 🔗 Fact Table | stg_aduana + dims | fact_aduana_item | 20 min | 04 |
| 5 | ✅ Validación | fact_aduana_item | 0 errores | 10 min | 05 |

**Total: ~1:20 horas de ejecución**

---

## Las 3 ideas clave

### 1️⃣ ETL: Extraer, Transformar, Cargar
```
EXTRAER        TRANSFORMAR       CARGAR
(del Excel)    (limpiar/unir)    (en DuckDB)
    ↓              ↓                 ↓
 Lee CSV      Quita espacios    stg_aduana
              Convierte fechas   dim_*
              Normaliza          fact_*
```

### 2️⃣ Star Schema: Una estrella con dimensiones
```
              dim_fecha
              dim_pais
              dim_producto
                 │
         ────────┼────────
         │                │
    dim_operacion    fact_aduana_item    dim_aduana
         │                │
         ────────┼────────
                 │
            dim_regimen
```

### 3️⃣ Datos sin repetir: IDs en lugar de texto
```
❌ MALO: "BRASIL" aparece 10,000 veces
✓ BUENO: El número "5" aparece 10,000 veces
         "5" apunta a "BRASIL" en dim_pais
```

---

## Antes vs Después

### ANTES (Excel desastre)
```
❌ Lento de abrir
❌ Difícil de buscar
❌ Datos inconsistentes
❌ Análisis manual
❌ Propenso a errores
```

### DESPUÉS (Data Warehouse)
```
✓ Rápido de consultar
✓ Búsquedas inteligentes
✓ Datos consistentes
✓ Análisis automático
✓ Confiable y auditado
```

---

## Los 5 documentos clave

```
1. PASO_A_PASO_DWH.md        ← EMPIEZA AQUÍ (2-3 horas)
   └─ Todo explicado paso a paso, humanizado

2. QUICK_START_DWH.md        ← O AQUÍ (20 minutos)
   └─ Versión rápida, solo lo esencial

3. DIAGRAMAS_DWH.md          ← PARA VISUALES
   └─ Flujos, esquemas, comparaciones

4. GUIA_DOCENTE.md           ← PARA PROFESORES
   └─ Cómo enseñar, secuencia de clases

5. ÍNDICE_GENERAL.md         ← NAVEGADOR
   └─ Tabla de contenidos, glosario, FAQ
```

---

## Los 6 archivos que creas

```
1. aduana.duckdb             ← Tu base de datos DW (se crea automáticamente)
                               • Contiene 15 tablas
                               • ~50 MB

2. fact_aduana_item.csv      ← Exportación de fact (opcional)
                               • Para Power BI si no tienes ODBC

3-5. dim_*.csv               ← Exportaciones de dimensiones (opcional)

6. Dash_DWH.pbix            ← Tu dashboard Power BI (lo creas tú)
                               • Reportes interactivos
                               • Gráficos y filtros
```

---

## Timeline de ejecución

```
T=0 min ──────────────────────────────────────────────────────── T=160 min
        │         │              │              │              │
        ├─ 15 min─┤ 20 min       │              │              │
        │ Struct  │ Staging      │ Dims (15)    │ Fact (20)    │ Valid (10)
        │ (01)    │ (02)         │ (03)         │ (04)         │ (05)
        │         │              │              │              │
        ✓ Start  ✓ Limpio       ✓ Catalogos   ✓ Conectado   ✓ Validado
```

---

## Conceptos en 10 líneas

| Concepto | En una línea |
|----------|-------------|
| **ETL** | Extraer datos, transformarlos, cargarlos en una BD |
| **DW** | Base de datos especial para análisis, no operaciones |
| **Bronze** | Datos originales sin procesar |
| **Silver** | Datos limpios pero sin organizar |
| **Gold** | Datos organizados listos para análisis |
| **Dimensión** | Tabla de referencia (catálogo sin repetir) |
| **Fact** | Tabla central con hechos y métricas |
| **StarSchema** | Diseño: tabla central + dimensiones alrededor |
| **FK** | Referencia de una tabla a otra |
| **JOIN** | Unir dos tablas por una clave común |

---

## El código en 3 pasos

### Paso 1: Conectar a DuckDB
```python
import duckdb
con = duckdb.connect('db/aduana.duckdb')
```

### Paso 2: Leer y transformar
```python
import pandas as pd
df = pd.read_excel('data_lake/bronze/DatosCSV.csv')
df = df.rename(columns=lambda x: x.strip().lower())
```

### Paso 3: Guardar en BD
```python
con.register('stg_aduana', df)
con.execute('INSERT INTO stg_aduana SELECT * FROM stg_aduana')
```

---

## Comandos essenciales (copiar/pegar)

```python
# Conectar
con = duckdb.connect('db/aduana.duckdb')

# Ver cuántas filas
con.query('SELECT COUNT(*) FROM stg_aduana').show()

# Ver estructura
con.query('SELECT * FROM stg_aduana LIMIT 1').show()

# Análisis rápido
con.query('''
SELECT 
    operacion,
    COUNT(*) as total,
    SUM(fob) as total_fob
FROM fact_aduana_item
GROUP BY operacion
''').show()

# Ver todas las tablas
con.query('''
SELECT name FROM sqlite_master 
WHERE type="table"
ORDER BY name
''').show()
```

---

## Checklist para saber si funcionó

- [ ] `01_Crear_Estructura_DW.ipynb` → Sin errores, 15 tablas creadas
- [ ] `02_Cargar_Staging.ipynb` → Sin errores, 41K filas en stg_aduana
- [ ] `03_Cargar_Dimensiones.ipynb` → Sin errores, 12 tablas con datos
- [ ] `04_Cargar_Fact_Table.ipynb` → Sin errores, 41K filas en fact_aduana_item
- [ ] `05_Validaciones.ipynb` → Todas las pruebas pasaron (✓)
- [ ] Power BI conectado a DuckDB
- [ ] Crear 3+ reportes en Power BI

---

## Diagnóstico rápido

| Síntoma | Causa | Solución |
|---------|-------|----------|
| "Table not found" | Notebook anterior no se ejecutó | Ejecuta 01, 02, 03 en orden |
| NULL en fact_table | FK sin coincidencia | Verifica dimensión correspondiente |
| Muy lento | Datos demasiados grandes | Filtrar en Power BI, no todo |
| ODBC no funciona | Driver no instalado | `pip install duckdb-odbc` |
| Errores de fecha | Formato inconsistente | Notebook 02 intenta normalizar |

---

## Después de completar (próximos pasos)

1. **Explora:** Abre el .duckdb en DBeaver y explora las tablas
2. **Reportea:** Crea 5+ reportes en Power BI
3. **Personaliza:** Modifica las columnas, agrega nuevas dimensiones
4. **Automatiza:** Crea un scheduler para ejecutar el ETL cada noche
5. **Escala:** Agrega más datos, más usuarios, publicación en Power BI Service

---

## Stack de tecnologías

```
┌─────────────────────────────────────────────────────────────┐
│                    POWER BI (Visualización)                 │
│              (reportes, dashboards, análisis)               │
└────────────────────────────┬────────────────────────────────┘
                             │
                    ODBC (conexión)
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   DUCKDB (Base de datos)                    │
│              (tablas, relaciones, índices)                  │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                PYTHON (Procesamiento ETL)                   │
│   (pandas, numpy, transformaciones de datos)                │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│            EXCEL / CSV (Fuente de datos)                    │
│          (datos originales sin procesar)                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Regla de oro

```
┌───────────────────────────────────────────────┐
│ NO cierres la conexión hasta terminar todo    │
│ NO ejecutes todo de una vez, ve celda a celda │
│ NO esperes que funcione si no hay datos       │
│ NO hagas cambios sin validar primero          │
│ SÍ  documenta cada error que encuentres       │
│ SÍ  valida después de cada paso               │
│ SÍ  pregunta si algo no tiene sentido         │
└───────────────────────────────────────────────┘
```

---

## Un minuto de contexto

**La realidad:** Tienes un archivo Excel con 40K+ filas de despachos aduanales.

**El problema:** Es imposible analizarlo directamente. Demasiado grande, desordenado, lento.

**La solución:** Construir un Data Warehouse: una base de datos especial donde:
- Los datos están limpios
- No hay repeticiones innecesarias
- Está optimizado para análisis
- Se puede conectar a Power BI

**El resultado:** Reportes rápidos, precisos, confiables que cualquiera puede usar.

**Tiempo:** 2-3 horas siguiendo este proyecto.

**Resultado final:** Un dashboard profesional en Power BI listo para compartir.

---

**Para empezar: 👉 [PASO_A_PASO_DWH.md](PASO_A_PASO_DWH.md)**

**Para resumir: 👉 [QUICK_START_DWH.md](QUICK_START_DWH.md)**

**Para ver diagramas: 👉 [DIAGRAMAS_DWH.md](DIAGRAMAS_DWH.md)**

