# 🎨 Visualización del DWH — Diagramas y flujos

**Guía visual para entender cómo funciona el Data Warehouse**

---

## 1. El flujo general (de inicio a fin)

```
┌─────────────────────────────────────────────────────────────────┐
│                        FASE 1: FUENTE                           │
│  Archivo Excel con datos desordenados (41,342 filas)            │
│  • Espacios en blanco                                            │
│  • Fechas como texto                                             │
│  • Información repetida                                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ ETL-Cargar-Staging.py (Notebook 02)
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASE 2: LIMPIEZA (STAGING)                         │
│  Tabla: stg_aduana (41,342 filas × 41 columnas)                 │
│  • Espacios quitados                                             │
│  • Fechas convertidas                                            │
│  • Todavía hay repeticiones (BRASIL 10,000 veces)               │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ ETL-Dimension.py (Notebook 03)
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│              FASE 3: DIMENSIONES (CATÁLOGOS)                    │
│                                                                 │
│  dim_operacion   dim_pais       dim_aduana     dim_producto    │
│  (2 filas)       (50 filas)     (8 filas)      (500 filas)     │
│                                                                 │
│  dim_destinacion dim_regimen    dim_canal      dim_fecha       │
│  (10 filas)      (20 filas)     (4 filas)      (730 filas)     │
│                                                                 │
│  dim_marca       dim_medio_transporte  dim_unidad_medida       │
│  (1000 filas)    (8 filas)             (12 filas)              │
│                                                                 │
│  dim_acuerdo                                                    │
│  (5 filas)                                                      │
│                                                                 │
│  ✓ Sin repeticiones                                             │
│  ✓ Cada uno es un catálogo limpio                              │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ ETL-FACT.py (Notebook 04)
                 │ 14 LEFT JOINs gigantescos
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│            FASE 4: TABLA DE HECHOS (FACT TABLE)                 │
│  Tabla: fact_aduana_item (41,342 filas × 33 columnas)           │
│                                                                 │
│  • id_fact (clave única)                                        │
│  • despacho_cifrado, item (clave de negocio)                   │
│  • 12 FK (id_operacion, id_pais_origen, id_producto, ...)      │
│  • 19 métricas (fob, cantidad_bultos, peso_total, ...)         │
│                                                                 │
│  ✓ Conectada a todas las dimensiones                            │
│  ✓ Datos limpios y normalizados                                 │
│  ✓ Optimizada para análisis                                     │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ ODBC (Power BI)
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               FASE 5: VISUALIZACIÓN                             │
│                                                                 │
│  Power BI conectado a DuckDB                                    │
│  • Reportes interactivos                                        │
│  • Slicers para filtrar                                         │
│  • Gráficos automáticos                                         │
│  • Análisis en tiempo real                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Zoom: ¿Qué pasa en Staging?

```
ANTES (Excel original)
┌──────────────────────────────────────────────────────────────────┐
│  Operacion    │   Pais Origen   │   Fecha Despacho   │  ...     │
├──────────────┼─────────────────┼────────────────────┤          │
│ IMPORTACION  │  BRA - BRASIL   │  "2023-01-15"      │  ...     │
│ IMPORTACION  │  BRA - BRASIL   │  "2023-01-16"      │  ...     │ ← BRASIL repetido
│  EXPORTACION │   CHN - CHINA   │  "2023-01-17"      │  ...     │
│ IMPORTACION  │  USA - ESTADOS  │  "2023-01-18"      │  ...     │
│ IMPORTACION  │  BRA - BRASIL   │  "2023-01-19"      │  ...     │ ← BRASIL repetido
└──────────────────────────────────────────────────────────────────┘

PROBLEMAS:
❌ Espacios en "  Operacion  " y "  Pais Origen  "
❌ Fechas como texto: "2023-01-15" (no es una fecha real)
❌ Repeticiones: BRASIL aparece 1000+ veces
❌ Formato extraño: "BRA - BRASIL" (dos partes mezcladas)

DESPUÉS (Staging)
┌──────────────────────────────────────────────────────────────────┐
│  operacion    │   pais_origen   │   fecha_despacho   │  ...     │
├───────────────┼─────────────────┼────────────────────┤          │
│ IMPORTACION   │   BRA - BRASIL  │   2023-01-15       │  ...     │
│ IMPORTACION   │   BRA - BRASIL  │   2023-01-16       │  ...     │
│ EXPORTACION   │   CHN - CHINA   │   2023-01-17       │  ...     │
│ IMPORTACION   │   USA - ESTADOS │   2023-01-18       │  ...     │
│ IMPORTACION   │   BRA - BRASIL  │   2023-01-19       │  ...     │
└──────────────────────────────────────────────────────────────────┘

MEJORAS:
✓ Espacios quitados de nombres de columnas
✓ Fechas convertidas a verdaderas fechas (2023-01-15, no "2023-01-15")
✓ Todavía hay repeticiones, pero están limpias
✓ Datos normalizados
```

---

## 3. Zoom: De Staging a Dimensiones

```
stg_aduana (41,342 filas)
│
├─ Columna "operacion"
│  ├─ IMPORTACION (20,000 veces)  ──► dim_operacion
│  └─ EXPORTACION  (21,342 veces)  │   ┌──────────────┐
│                                   │   │ id │ operacion│
│                                   │   ├─────┼───────────┤
│                                   └──►│ 1  │IMPORTACION│
│                                      │ 2  │EXPORTACION│
│                                      └────────────────┘
│
├─ Columna "pais_origen" + "pais_destino"
│  ├─ "BRA - BRASIL"  (5,000 veces)  ──► dim_pais
│  ├─ "CHN - CHINA"   (4,000 veces)  │   ┌────┬──────┬──────────────┐
│  ├─ "USA - USA"     (3,000 veces)  │   │ id │ cod  │ pais_nombre  │
│  └─ ... + 47 países más ...        │   ├─────┼──────┼──────────────┤
│                                    └──►│ 1  │ BRA  │ BRASIL       │
│                                       │ 2  │ CHN  │ CHINA        │
│                                       │ 3  │ USA  │ USA          │
│                                       │... │ ...  │ ...          │
│                                       └────┴──────┴──────────────┘
│
└─ Columna "posicion_arancelaria"
   ├─ "01.01.01" (500 veces)  ──► dim_producto
   ├─ "01.01.02" (300 veces)  │   ┌───┬──────────┬──────────────────┐
   └─ ... + 498 productos ...  │   │id │hs_code   │ descripcion      │
                               │   ├───┼──────────┼──────────────────┤
                               └──►│1  │01.01.01  │ GANADO VIVO      │
                                  │2  │01.01.02  │ CABALLOS VIVOS   │
                                  │..│ ...      │ ...              │
                                  └───┴──────────┴──────────────────┘

RESULTADO:
✓ dim_operacion: 2 filas (sin repetir)
✓ dim_pais: 50 filas (sin repetir)
✓ dim_producto: 500 filas (sin repetir)
```

---

## 4. El Star Schema (Esquema en Estrella)

```
                         ┌─────────────┐
                         │  dim_fecha  │
                         │  (730 filas)│
                         └──────┬──────┘
                                │
                         ┌──────┴──────┐
                         │ id_fecha_*  │ (fecha_despacho, fecha_vto_pago)
                         │ (2 FKs)     │
                         │             │
        ┌─────────────┐  │             │  ┌──────────────┐
        │ dim_pais    │  │             │  │ dim_producto │
        │ (50 filas)  │  │             │  │ (500 filas)  │
        └────┬────────┘  │             │  └──────┬───────┘
             │           │             │         │
             │           │             │         │
       ┌─────┴──────────▼─┴─────────────┴────────┴────────────┐
       │                                                      │
       │           ★ fact_aduana_item ★                      │
       │           (41,342 filas)                            │
       │                                                      │
       │  • id_fact (PK)                                     │
       │  • despacho_cifrado, item (clave natural)           │
       │  • id_operacion (FK → dim_operacion)                │
       │  • id_pais_origen (FK → dim_pais)                   │
       │  • id_pais_destino (FK → dim_pais)                  │
       │  • id_producto (FK → dim_producto)                  │
       │  • id_aduana (FK → dim_aduana)                      │
       │  • id_fecha_despacho (FK → dim_fecha)               │
       │  • id_fecha_vto_pago (FK → dim_fecha)               │
       │  • ... más FKs ...                                  │
       │  • fob, cantidad_bultos, peso_total, ...            │
       │                                                      │
       └─────┬──────────▲─┬─────────────┬────────┬───────────┘
             │           │ │             │        │
        ┌────┴────┐  ┌────┴─┴────┐  ┌────┴──┐   ┌┴─────────────┐
        │dim_      │  │ dim_      │  │dim_   │   │ dim_marca   │
        │operacion │  │destinacion│  │regimen│   │ (1000 filas)│
        │(2 filas) │  │(10 filas) │  │(20f.)│   └─────────────┘
        └──────────┘  └───────────┘  └──────┘
        
        ┌──────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │dim_aduana    │  │dim_canal         │  │dim_medio_transporte
        │(8 filas)     │  │(4 filas)         │  │(8 filas)
        └──────────────┘  └──────────────────┘  └──────────────────┘
        
        ┌────────────────────┐  ┌──────────────┐
        │dim_unidad_medida   │  │dim_acuerdo   │
        │(12 filas)          │  │(5 filas)     │
        └────────────────────┘  └──────────────┘

POR QUÉ ESTO ES MEJOR:

OPCIÓN A: Todo en una tabla (❌ MALO)
┌─────────────────────────────────────────────────────────────────┐
│despacho│item│operacion │pais_origen │pais_dest │producto │...  │
├────────┼────┼──────────┼────────────┼──────────┼─────────┤     │
│...     │... │IMPORTA.  │BRA-BRASIL  │ARG-ARG   │01.01.01 │...  │
│...     │... │IMPORTA.  │BRA-BRASIL  │ARG-ARG   │01.01.01 │...  │ ← Repetición
│...     │... │IMPORTA.  │BRA-BRASIL  │CHI-CHILE │01.01.02 │...  │
│...     │... │EXPORTA.  │ARG-ARG     │BRA-BRASIL│01.01.01 │...  │
│...     │... │IMPORTA.  │BRA-BRASIL  │ARG-ARG   │01.01.01 │...  │ ← Repetición
└─────────────────────────────────────────────────────────────────┘
Problemas:
- Muchas repeticiones (lento)
- Base de datos gigante
- Si "BRASIL" cambia, actualizar 10,000 veces

OPCIÓN B: Star Schema (✓ BUENO)
fact_aduana_item:
┌──────┬──────┬─────────┬────────────┬────────────┬──────────┐
│ id_f │ id_op│ id_pais_│id_pais_dest│ id_producto│ ...      │
│ act  │ erac │ origin  │            │            │          │
├──────┼──────┼─────────┼────────────┼────────────┼──────────┤
│ 1    │ 1    │ 1       │ 2          │ 1          │ ...      │
│ 2    │ 1    │ 1       │ 2          │ 1          │ ...      │
│ 3    │ 1    │ 1       │ 3          │ 2          │ ...      │
│ 4    │ 2    │ 2       │ 1          │ 1          │ ...      │
│ 5    │ 1    │ 1       │ 2          │ 1          │ ...      │
└──────┴──────┴─────────┴────────────┴────────────┴──────────┘

dim_pais:
┌─────┬──────┬─────────┐
│ id  │ cod  │ nombre  │
├─────┼──────┼─────────┤
│ 1   │ BRA  │ BRASIL  │
│ 2   │ ARG  │ ARGENTINA│
│ 3   │ CHI  │ CHILE   │
└─────┴──────┴─────────┘

Ventajas:
- Menos repeticiones (rápido)
- Base de datos pequeña
- Si "BRASIL" cambia, actualizar 1 sola vez
```

---

## 5. Proceso de JOIN (fusión de tablas)

```
PASO 1: Tenemos stg_aduana con texto
┌────────────────────────────────────────┐
│ despacho │ operacion    │ pais_origen  │
├──────────┼──────────────┼──────────────┤
│ D001     │ IMPORTACION  │ BRA - BRASIL │
│ D002     │ EXPORTACION  │ CHN - CHINA  │
│ D003     │ IMPORTACION  │ USA - USA    │
└────────────────────────────────────────┘

PASO 2: Extraemos los IDs de dim_operacion
┌──────────────────────────────┐
│ id  │ operacion   │           │
├─────┼─────────────┤           │
│ 1   │ IMPORTACION │           │
│ 2   │ EXPORTACION │           │
└──────────────────────────────┘
         ▲                  ▲
         │                  │
         └────────────────┬─┘
                          │
                    LEFT JOIN

PASO 3: El JOIN busca coincidencias
┌────────────────────────────────────────────────────────────────┐
│ stg.despacho │ stg.operacion    │ dim.id_operacion │           │
├──────────────┼──────────────────┼──────────────────┤           │
│ D001         │ IMPORTACION  ────►──────► 1         │ ✓ Encontrado
│ D002         │ EXPORTACION  ────►──────► 2         │ ✓ Encontrado
│ D003         │ IMPORTACION  ────►──────► 1         │ ✓ Encontrado
│ D004         │ (NULL)       ────►──────► NULL      │ ✗ No encontrado
└────────────────────────────────────────────────────────────────┘

RESULTADO: Una tabla unida
┌──────────┬──────────────┬────────────┐
│despacho  │operacion_txt │id_operacion│
├──────────┼──────────────┼────────────┤
│ D001     │IMPORTACION   │ 1          │
│ D002     │EXPORTACION   │ 2          │
│ D003     │IMPORTACION   │ 1          │
│ D004     │(NULL)        │ NULL       │
└──────────┴──────────────┴────────────┘
```

---

## 6. Ciclo de vida de los datos

```
TIME LINE:
t=0 ──────────────────────────────────────────────────────────► t=∞

    Generación          Extracción         Transformación        Análisis
        │                   │                    │                  │
    ┌───▼────┐         ┌────▼──┐          ┌─────▼─────┐        ┌───▼────┐
    │ Aduana │         │ Excel │          │ DuckDB    │        │Power BI│
    │ Recibe │ ──────► │       │ ───────► │ DW        │ ──────► │Reports │
    │ datos  │         │       │          │           │        │        │
    └────────┘         └───────┘          └───────────┘        └────────┘
        ▲                   ▲                   ▲                    ▲
        │                   │                   │                    │
    Real                 Bronze           Silver + Gold          Insights
    (Raw)               (Source)          (Processed)            (Actions)
```

---

## 7. Comparación: Antes vs Después

```
ANTES (sin DW):
┌──────────────────────────────────────┐
│          Excel Original              │
│  41,342 filas × 50+ columnas         │
│  • Espacios en blanco                │
│  • Fechas como texto                 │
│  • Producto repetido 1000+ veces     │
│  • País repetido 10,000+ veces       │
│  • Lento de abrir                    │
│  • Difícil de analizar               │
│  • Propenso a errores                │
└──────────────────────────────────────┘
            │
            │ Abrir en Power BI
            ▼
    ❌ Reportes lentos
    ❌ Dificultad para filtrar
    ❌ Análisis incompletos


DESPUÉS (con DW):
┌──────────────────────────────────────┐
│      Data Warehouse (DuckDB)         │
│  • 1 tabla de staging (limpio)       │
│  • 12 tablas de dimensiones (índices)│
│  • 1 tabla de hechos (conectada)     │
│  • Datos normalizados                │
│  • Sin repeticiones innecesarias     │
│  • Rápido de procesar                │
│  • Fácil de analizar                 │
│  • Estructura clara                  │
└──────────────────────────────────────┘
            │
            │ Conectar en Power BI
            ▼
    ✓ Reportes rápidos
    ✓ Filtros inteligentes
    ✓ Análisis profundos
    ✓ Reusable y escalable
```

---

## 8. Las 4 capas de datos

```
CAPAS DEL DATA LAKE:

CAPA BRONZE (Raw Data)
┌──────────────────────────────────┐
│ Datos crudos tal como vienen     │
│ • Excel original                 │
│ • CSVs sin procesar              │
│ • Datos "sucios"                 │
│ Usar para: auditoría, trazabilidad
└──────────────────────────────────┘

         ↓ ETL

CAPA SILVER (Staging / Refined)
┌──────────────────────────────────┐
│ Datos limpios pero no organizados │
│ • Sin espacios en blanco         │
│ • Fechas convertidas             │
│ • Aún hay repeticiones           │
│ Usar para: análisis ad-hoc       │
└──────────────────────────────────┘

         ↓ ETL

CAPA GOLD (Analytics Ready)
┌──────────────────────────────────┐
│ Datos listos para análisis       │
│ • Tablas dimensiones normalizadas │
│ • Tabla de hechos optimizada     │
│ • Relaciones claras              │
│ • Sin redundancias               │
│ Usar para: reportes, BI, análisis│
└──────────────────────────────────┘

         ↓ Conexión ODBC

VISUALIZACIÓN
┌──────────────────────────────────┐
│ Power BI                         │
│ • Reportes interactivos          │
│ • Dashboards                     │
│ • Insights de negocio            │
└──────────────────────────────────┘
```

---

## 9. Relaciones (ForeignKeys)

```
IMAGINA QUE TIENES:

fact_aduana_item
├─ despacho_cifrado: "D001"
├─ id_operacion: 1
├─ id_pais_origen: 5
└─ fob: $10,000

El id_operacion=1 APUNTA A:
    dim_operacion
    ├─ id_operacion: 1
    └─ operacion: "IMPORTACION"

El id_pais_origen=5 APUNTA A:
    dim_pais
    ├─ id_pais: 5
    ├─ codigo: "BRA"
    └─ pais_nombre: "BRASIL"

RESULTADO: Cuando lees fact_aduana_item en Power BI,
ves que el despacho D001 es una IMPORTACION de BRASIL por $10,000
```

---

## 10. Resumen visual de archivos

```
Proyecto aduana_bi/
│
├─ 📂 notebooks/                      ← EJECUTA ESTOS EN ORDEN
│  ├─ 00_Arquitectura_y_Conceptos.ipynb   (Leer, no ejecutar)
│  ├─ 01_Crear_Estructura_DW.ipynb        (Ejecutar 1ro)
│  ├─ 02_Cargar_Staging.ipynb             (Ejecutar 2do)
│  ├─ 03_Cargar_Dimensiones.ipynb         (Ejecutar 3ro)
│  ├─ 04_Cargar_Fact_Table.ipynb          (Ejecutar 4to)
│  └─ 05_Validaciones.ipynb               (Ejecutar 5to)
│
├─ 📂 db/
│  └─ aduana.duckdb                   ← TU DATA WAREHOUSE
│                                       (se crea automáticamente)
│
├─ 📂 data_lake/
│  ├─ bronze/                         ← Datos originales
│  │  └─ DatosCSV.csv
│  ├─ silver/                         ← Staging (opcional)
│  └─ gold/                           ← Fact table (opcional)
│
├─ 📂 etl/
│  └─ (Scripts Python, referencia)
│
├─ PASO_A_PASO_DWH.md                ← ⭐ LEE PRIMERO (completo)
├─ QUICK_START_DWH.md                ← ⭐ O ESTO (rápido)
└─ PBI/
   └─ Dash_DWH.pbix                  ← Power BI (crear aquí)
```

---

Esta guía visual complementa los documentos textuales. Para detalles completos, lee **PASO_A_PASO_DWH.md**.

