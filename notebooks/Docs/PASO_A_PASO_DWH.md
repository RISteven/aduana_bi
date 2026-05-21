# 🏗️ Armado del Data Warehouse — Guía Paso a Paso

**Para:** Analistas, profesores y estudiantes que quieran entender cómo construir un Data Warehouse desde cero

**Duración:** aproximadamente 6-8 horas (puede hacerse en varias sesiones)

**Resultado final:** Un Data Warehouse completo listo para conectar a Power BI

---

## 📋 Tabla de Contenidos

1. [Preparación del entorno](#1-preparación-del-entorno)
2. [Entender el problema y la solución](#2-entender-el-problema-y-la-solución)
3. [Crear la estructura de las tablas (Fase 1: Arquitectura)](#3-crear-la-estructura-de-las-tablas)
4. [Cargar y limpiar los datos (Fase 2: Staging)](#4-cargar-y-limpiar-los-datos)
5. [Crear las dimensiones (Fase 3: Dimensiones)](#5-crear-las-dimensiones)
6. [Crear la tabla de hechos (Fase 4: Fact Table)](#6-crear-la-tabla-de-hechos)
7. [Validar la integridad (Fase 5: Validaciones)](#7-validar-la-integridad)
8. [Conectar a Power BI (Fase 6: Visualización)](#8-conectar-a-power-bi)

---

## 1. Preparación del entorno

### ¿Qué necesitas?

Antes de empezar, asegúrate de tener:

- **Python 3.9 o superior** instalado
- **Un editor de código** (VS Code recomendado)
- **Jupyter Notebook o Jupyter Lab** (para ejecutar los notebooks)
- **Las librerías necesarias** (las instalaremos juntos)

### Paso 1.1: Instalar las librerías

Abre tu terminal/PowerShell y ejecuta:

```bash
pip install duckdb pandas openpyxl jupyterlab
```

Esto instala:
- **duckdb**: la base de datos donde guardamos nuestro DW
- **pandas**: herramienta para manipular datos en Python
- **openpyxl**: para leer archivos Excel
- **jupyterlab**: para ejecutar los notebooks de forma interactiva

### Paso 1.2: Verificar la instalación

```bash
python -c "import duckdb; import pandas; print('¡Todo listo!')"
```

Si ves "¡Todo listo!" significa que todo está bien. Si hay error, revisa que la instalación fue correcta.

### Paso 1.3: Descargar el proyecto

Si aún no lo has hecho:

```bash
git clone https://github.com/RISteven/aduana_bi.git
cd aduana_bi
```

---

## 2. Entender el problema y la solución

### ¿Cuál es el problema?

Imagina que trabajas en una Aduana y tienes un archivo Excel gigante con información de todos los despachos (importaciones y exportaciones):

- Columnas con espacios en blanco que causan problemas
- Fechas escritas como texto en lugar de verdaderas fechas
- Información repetida (el mismo país aparece 1000 veces)
- Datos en diferentes formatos y sin normalizar

**Si intentas analizar esto directamente en Power BI, tendrás:**
- Reportes lentos
- Dificultad para buscar y agrupar
- Errores de duplicación
- Análisis incompletos

### ¿Cuál es la solución?

Construimos un **Data Warehouse (DW)**: una base de datos especialmente diseñada para análisis.

En lugar de tener un Excel caótico, tenemos:

1. **Datos limpios y organizados**
2. **Tablas de referencia** (países, aduanas, operaciones)
3. **Una tabla central** con los hechos reales (el despacho de cada producto)
4. **Relaciones claras** entre todas las tablas

**Resultado:** reportes rápidos, precisos y confiables en Power BI.

### Analogía para entenderlo

Piensa en un supermercado:

- **Excel original** = un almacén desordenado donde todo está mezclado
- **Data Warehouse** = un supermercado bien organizado con pasillos, categorías, y un sistema de inventario preciso
- **Power BI** = el cliente que necesita hacer compras rápidamente

En el almacén caótico, buscar algo toma horas. En el supermercado organizado, lo encuentras en minutos.

---

## 3. Crear la estructura de las tablas

**Tiempo estimado:** 30 minutos

### ¿Qué hacemos en este paso?

Creamos todas las tablas que necesitamos, pero **vacías**. Es como construir las habitaciones de una casa antes de traer los muebles.

### El modelo que usaremos

Usamos un diseño llamado **Star Schema** (esquema en estrella):

```
                      dim_fecha
                         │
                         │
dim_pais ─────────┬──► dim_producto ◄─────┬────── dim_marca
                  │                        │
            fact_aduana_item  ◄──────────┬─┘
                  │                      │
dim_operacion ────┼──► dim_destinacion  │
                  │                      │
dim_aduana ───────┼──► dim_regimen ◄────┘
                  │
            dim_canal
            │
      dim_medio_transporte
            │
      dim_unidad_medida
            │
      dim_acuerdo
```

**¿Qué significa esto?**

- El cuadrado del centro (**fact_aduana_item**) es la tabla principal. Contiene todos los despachos.
- Los cuadrados alrededor (**dim_***) son tablas de referencia. Contienen datos descriptivos.
- Las flechas son relaciones: cada despacho está relacionado con una aduana, un país, un producto, etc.

### Paso 3.1: Abrirse el notebook 01

Abre el archivo: `notebooks/01_Crear_Estructura_DW.ipynb`

Este notebook ejecuta un script que:
1. Borra las tablas antiguas (si existen)
2. Crea 15 tablas nuevas y vacías
3. Define claves primarias y extranjeras

### Paso 3.2: Entender las tablas de dimensiones

Cada tabla `dim_*` contiene un catálogo:

| Tabla | Contiene | Ejemplo de datos |
|-------|----------|------------------|
| `dim_operacion` | Tipos de operación aduanal | IMPORTACION, EXPORTACION, etc |
| `dim_pais` | Lista de países | BRASIL, CHINA, USA, etc |
| `dim_aduana` | Aduanas del país | EZEIZA, PUERTO, etc |
| `dim_destinacion` | Destinos de mercancía | CONSUMO, DEPOSITO, etc |
| `dim_producto` | Productos según clasificación | HS Code 01.01.01 GANADO VIVO |
| `dim_fecha` | Atributos de fechas | Día, mes, año, trimestre |

Cada tabla tiene una columna `id_*` que es el identificador único (1, 2, 3, ...). Esta es la "llave" que usaremos para conectar con la tabla central.

### Paso 3.3: Ejecutar el notebook

En el notebook, ejecuta la primera celda (busca el botón ▶️ o presiona Shift+Enter):

```python
import duckdb
con = duckdb.connect('db/aduana.duckdb')
# Crear todas las tablas...
```

**¿Qué deberías ver?**
- Sin errores
- Un mensaje que diga algo como "15 tablas creadas"

**Si hay error:**
- Verifica que la carpeta `db/` existe
- Verifica que tienes permisos de escritura en esa carpeta
- Revisa el mensaje de error (es tu amigo, no tu enemigo)

---

## 4. Cargar y limpiar los datos

**Tiempo estimado:** 1 hora

### ¿Qué hacemos en este paso?

Leemos el Excel original (los datos "sucios"), los limpiamos y los guardamos en la tabla `stg_aduana` (Staging = zona de paso).

**Analógicamente:** es como lavar la ropa antes de guardarla en el armario.

### ¿Cuáles son los problemas que enfrentamos?

1. **Columnas con espacios:** `" Operacion "` en lugar de `"Operacion"`
2. **Fechas como texto:** `"2023-01-15"` (texto) en lugar de verdaderas fechas
3. **Valores NULL:** campos vacíos que necesitan un valor por defecto
4. **Espacios en blanco:** valores como `" BRASIL "` en lugar de `"BRASIL"`

### Paso 4.1: Abre el notebook 02

Abre: `notebooks/02_Cargar_Staging.ipynb`

Este notebook:
1. Lee el Excel
2. Renombra todas las columnas (quita espacios)
3. Convierte fechas de texto a verdaderas fechas
4. Limpia espacios en blanco
5. Guarda todo en la tabla `stg_aduana`

### Paso 4.2: Entender el proceso de limpieza

**Lectura del Excel:**
```python
excel_file = 'data_lake/bronze/DatosCSV.csv'
df = pd.read_excel(excel_file)  # Lee el archivo
print(df.head())  # Muestra las primeras 5 filas
```

**Renombrar columnas:**
```python
df = df.rename(columns={
    ' Operacion ': 'operacion',        # Quita espacios y minúsculas
    ' Pais Origen ': 'pais_origen',
    # ... más columnas
})
```

**Convertir fechas:**
```python
df['fecha_despacho'] = pd.to_datetime(
    df['fecha_despacho'], 
    errors='coerce'  # Si hay error, pone NULL en lugar de fallar
)
```

**Limpiar espacios:**
```python
df['pais_origen'] = df['pais_origen'].str.strip()  # Quita espacios al inicio/final
```

### Paso 4.3: Ejecutar el notebook

1. Ve a la celda que dice `# Paso 1: Leer el Excel`
2. Ejecuta esa celda (presiona Shift+Enter)
3. Ve viendo los resultados: `print()` mostrará las primeras filas

**Consejos:**
- Ejecuta **celda por celda**, no todo de una vez
- Después de cada celda, lee el resultado y asegúrate de que tenga sentido
- Si ves una celda que dice `print(df.isnull().sum())`, verás cuántos NULLs hay en cada columna

### Paso 4.4: Verificar que los datos se cargaron

Al final del notebook, deberías ver un mensaje similar a:

```
✓ 41,342 filas cargadas en stg_aduana
✓ 41 columnas
✓ 0 errores de fecha
```

Si no ves esto:
- Verifica que el archivo Excel existe en `data_lake/bronze/`
- Verifica que la conexión a DuckDB está abierta
- Lee el mensaje de error (suele ser muy descriptivo)

---

## 5. Crear las dimensiones

**Tiempo estimado:** 1.5 horas

### ¿Qué hacemos en este paso?

Tomamos la tabla `stg_aduana` (caótica, con datos repetidos) y creamos 12 tablas de referencia (dimensiones) **limpias y sin duplicados**.

**Analógicamente:** es como tomar un archivo desordenado y crear carpetas bien etiquetadas.

### ¿Por qué hacemos esto?

Si guardamos directamente el texto en la tabla de hechos:

- **BRAZIL** aparece 10,000 veces (repetición innecesaria)
- Si el nombre cambia, tenemos que actualizar 10,000 registros

Si creamos una tabla `dim_pais`:

- **BRAZIL** aparece 1 sola vez con `id_pais = 5`
- La tabla de hechos guarda solamente el número 5 (mucho más pequeño)
- Si el nombre cambia, actualizamos 1 sola vez

**Ventaja:** base de datos más rápida, más pequeña y más fácil de mantener.

### Paso 5.1: Abre el notebook 03

Abre: `notebooks/03_Cargar_Dimensiones.ipynb`

Este notebook crea todas las dimensiones:

```sql
-- Ejemplo: dim_operacion
SELECT DISTINCT operacion
FROM stg_aduana
ORDER BY operacion
```

De cada columna única en staging, creamos un ID numérico:

```sql
SELECT 
    ROW_NUMBER() OVER (ORDER BY operacion) as id_operacion,
    operacion
FROM (
    SELECT DISTINCT operacion FROM stg_aduana
) distinct_ops
```

**¿Qué significa `ROW_NUMBER()`?** Es una función que numera las filas: 1, 2, 3, 4, ...

### Paso 5.2: Las 12 dimensiones que crearemos

| Dimensión | ¿De dónde sacamos los datos? | ¿Cuántas filas aprox? |
|-----------|------------------------------|----------------------|
| `dim_operacion` | Columna `operacion` | 2 (IMPORTACION, EXPORTACION) |
| `dim_pais` | Columna `pais_origen` + `pais_destino` | 50+ |
| `dim_aduana` | Columna `aduana` | 8 |
| `dim_producto` | Columna `posicion_arancelaria` | 500+ |
| `dim_destinacion` | Columna `destinacion` | 5-10 |
| `dim_regimen` | Columna `regimen` | 10+ |
| `dim_canal` | Columna `canal` | 3-4 |
| `dim_medio_transporte` | Columna `medio_transporte` | 5-10 |
| `dim_unidad_medida` | Columna `unidad_medida` | 10+ |
| `dim_acuerdo` | Columna `acuerdo` | 3-5 |
| `dim_marca` | Columna `marca` | 1000+ |
| `dim_fecha` | Fechas entre min y max de `fecha_despacho` | 365 (1 año) o 730 (2 años) |

### Paso 5.3: Ejecutar el notebook 03

Ejecuta celda por celda. Después de cada una, verifica:

```python
con.query('SELECT COUNT(*) FROM dim_operacion').show()
# Deberías ver algo como: 2 filas
```

### Paso 5.4: Un ejemplo detallado: `dim_pais`

Este es un caso especial porque usamos una función llamada `SPLIT_PART`:

```sql
SELECT DISTINCT 
    SPLIT_PART(pais_origen, ' - ', 1) as codigo,
    SPLIT_PART(pais_origen, ' - ', 2) as pais_nombre
FROM stg_aduana
WHERE pais_origen IS NOT NULL
ORDER BY pais_nombre
```

**¿Qué significa?**

Si el campo contiene `"BRA - BRASIL"`:
- `SPLIT_PART(..., ' - ', 1)` = `"BRA"` (primera parte)
- `SPLIT_PART(..., ' - ', 2)` = `"BRASIL"` (segunda parte)

Es útil porque el Excel original tiene ambas partes juntas, y queremos separarlas.

---

## 6. Crear la tabla de hechos

**Tiempo estimado:** 1.5 horas

### ¿Qué hacemos en este paso?

Tomar la tabla `stg_aduana` (con texto repetido) y crear `fact_aduana_item` (con IDs numéricos y relaciones claras).

**Analógicamente:** es como tomar un documento desordenado y crear un índice donde todo está conectado.

### El proceso: 14 JOINs enormes

La tabla de hechos se crea haciendo LEFT JOINs con cada una de las 12 dimensiones:

```sql
SELECT 
    stg.despacho_cifrado,
    stg.item,
    
    -- Buscar el id_operacion en dim_operacion
    do.id_operacion,
    
    -- Buscar el id_pais_origen en dim_pais (para país de origen)
    dpo.id_pais as id_pais_origen,
    
    -- Buscar el id_pais_destino en dim_pais (para país de destino)
    dpd.id_pais as id_pais_destino,
    
    -- ... más JOINs ...
    
    -- Las métricas numéricas del despacho
    stg.fob,
    stg.cantidad_bultos,
    stg.peso_total
    
FROM stg_aduana stg
LEFT JOIN dim_operacion do 
    ON stg.operacion = do.operacion
LEFT JOIN dim_pais dpo 
    ON SPLIT_PART(stg.pais_origen, ' - ', 2) = dpo.pais_nombre
-- ... más JOINs ...
```

**¿Qué significa `LEFT JOIN`?**

Mantiene todas las filas de `stg_aduana`, aunque no encuentre coincidencia en la dimensión. Si no hay match, pone NULL en el ID de la dimensión.

Esto es importante porque queremos mantener todos los despachos, incluso si hay datos incompletos.

### Paso 6.1: Abre el notebook 04

Abre: `notebooks/04_Cargar_Fact_Table.ipynb`

Este notebook:
1. Crea la tabla `fact_aduana_item` con un gigantesco JOIN
2. Rellena campos como `id_fecha_despacho`, `id_fecha_vto_pago`, etc.

### Paso 6.2: El código completo del JOIN

No te asustes si ves mucho código. La estructura es:

1. **SELECT**: elige qué columnas guardar
2. **FROM stg_aduana**: tabla de origen
3. **14 x LEFT JOIN**: busca el ID en cada dimensión
4. **INSERT INTO fact_aduana_item**: guarda el resultado

### Paso 6.3: Ejecutar el notebook

Ejecuta celda por celda. Después de ejecutar la creación, verifica:

```python
con.query('SELECT COUNT(*) FROM fact_aduana_item').show()
```

**¿Cuántas filas deberías ver?**

Aproximadamente igual a `stg_aduana` (porque usamos LEFT JOIN). Si `stg_aduana` tiene 41,342 filas, `fact_aduana_item` debería tener ~41,342 filas también.

### Paso 6.4: Verificar que los JOINs funcionaron

```python
con.query('''
SELECT 
    id_operacion,
    id_pais_origen,
    id_producto,
    COUNT(*) as total
FROM fact_aduana_item
GROUP BY id_operacion, id_pais_origen, id_producto
ORDER BY total DESC
LIMIT 10
''').show()
```

Esto te muestra los despachos más frecuentes. Si ves números (no NULLs), significa que los JOINs funcionaron.

---

## 7. Validar la integridad

**Tiempo estimado:** 45 minutos

### ¿Qué hacemos en este paso?

Verificamos que:
1. ✓ Los datos son correctos
2. ✓ No hay datos huérfanos (FK sin correspondencia)
3. ✓ No hay datos faltantes críticos
4. ✓ Los números tienen sentido

**Analógicamente:** es como revisar que cada ladrillo de la casa está bien colocado.

### Paso 7.1: Abre el notebook 05

Abre: `notebooks/05_Validaciones.ipynb`

Este notebook ejecuta una serie de validaciones.

### Paso 7.2: Las 10 validaciones principales

**Validación 1: ¿Hay FKs huérfanas?**

```python
con.query('''
SELECT COUNT(*) as huerfanas
FROM fact_aduana_item
WHERE id_operacion IS NULL
''').show()
```

Si hay NULLs, significa que hay despachos cuya operación no está en `dim_operacion`. Esto es un problema.

**Validación 2: ¿Hay duplicados en las claves?**

```python
con.query('''
SELECT despacho_cifrado, item, COUNT(*) as veces
FROM fact_aduana_item
GROUP BY despacho_cifrado, item
HAVING veces > 1
''').show()
```

Si ves que algo aparece 2+ veces, hay un problema (la clave debería ser única).

**Validación 3: ¿Hay valores negativos donde no deberían?**

```python
con.query('''
SELECT COUNT(*) as valores_negativos
FROM fact_aduana_item
WHERE fob < 0
''').show()
```

Los importes negativos no tienen sentido. Si hay, hay un problema en los datos.

**Validación 4: ¿El total de filas es razonable?**

```python
con.query('''
SELECT 
    (SELECT COUNT(*) FROM stg_aduana) as staging,
    (SELECT COUNT(*) FROM fact_aduana_item) as fact
''').show()
```

Deberían ser casi iguales. Si `fact_aduana_item` tiene muchas menos filas, hay un problema.

**Validación 5: ¿Las fechas son razonables?**

```python
con.query('''
SELECT 
    MIN(fecha_despacho) as fecha_minima,
    MAX(fecha_despacho) as fecha_maxima,
    COUNT(*) as total
FROM fact_aduana_item
WHERE fecha_despacho IS NOT NULL
''').show()
```

Verifica que las fechas tengan sentido (no futura, no muy antigua).

### Paso 7.3: Interpretación de resultados

**Si todo está bien:**
```
✓ 0 FKs huérfanas
✓ 0 duplicados
✓ 0 valores negativos
✓ Fact tiene 41,342 filas (como staging)
✓ Fechas entre 2023-01-01 y 2024-12-31
```

**Si hay problemas:**
- Documenta el problema
- Vuelve al paso anterior (fact table o dimensiones)
- Revisa el código donde se crea esa dimensión
- Ejecuta nuevamente

### Paso 7.4: Ejecutar todas las validaciones

Ejecuta celda por celda. Si todas dicen "✓ PASADO", estás listo para Power BI.

---

## 8. Conectar a Power BI

**Tiempo estimado:** 30 minutos

### ¿Qué hacemos en este paso?

Abrimos Power BI, conectamos a nuestro archivo `aduana.duckdb` y creamos reportes.

### Paso 8.1: Descargar Power BI

Si aún no tienes Power BI:

1. Ve a https://powerbi.microsoft.com
2. Descarga "Power BI Desktop"
3. Instálalo
4. Abrelo

### Paso 8.2: Conectar DuckDB a Power BI

**Opción A: ODBC (recomendado)**

1. Instala el driver ODBC de DuckDB:
   ```bash
   pip install duckdb-odbc
   ```

2. En Power BI, ve a `File → Get Data → ODBC`

3. Selecciona "duckdb_driver" o similar

4. Configura:
   - **Host/File:** `C:\Información\proyectos\aduana_bi\db\aduana.duckdb`
   - **Database:** (dejar vacío)

5. Click en "Connect"

**Opción B: Copiar CSV desde DuckDB**

Si ODBC no funciona, exporta las tablas a CSV:

```python
con = duckdb.connect('db/aduana.duckdb')
con.query('SELECT * FROM fact_aduana_item').to_df().to_csv('fact_aduana_item.csv', index=False)
```

Luego importa los CSVs en Power BI (`File → Get Data → CSV`).

### Paso 8.3: Crear relaciones en Power BI

Una vez que tengas los datos en Power BI:

1. Ve a la pestaña `Model`
2. Arrastra relaciones:
   - `fact_aduana_item.id_operacion` ↔ `dim_operacion.id_operacion`
   - `fact_aduana_item.id_pais_origen` ↔ `dim_pais.id_pais`
   - `fact_aduana_item.id_producto` ↔ `dim_producto.id_producto`
   - ... (más relaciones)

Power BI debería detectar automáticamente muchas de ellas.

### Paso 8.4: Crear visualizaciones

**Ejemplo 1: Total FOB por operación**

1. Nueva página
2. Arrastra `dim_operacion.operacion` al canvas
3. Arrastra `fact_aduana_item.fob` (suma)
4. Crea un gráfico de barras

**Ejemplo 2: Top 10 países**

1. Nueva página
2. Arrastra `dim_pais.pais_nombre` al canvas
3. Arrastra `fact_aduana_item.cantidad_bultos` (suma)
4. Filtra para los Top 10

**Ejemplo 3: Tendencia por fecha**

1. Nueva página
2. Arrastra `dim_fecha.fecha` al canvas
3. Arrastra `fact_aduana_item.fob` (suma)
4. Crea un gráfico de línea

### Paso 8.5: Guardar y compartir

1. `File → Save`
2. Guarda como `Dash_DWH.pbix`
3. Sube a Power BI Service (online) si lo deseas

---

## 📊 Checklist de completitud

Usa este checklist para verificar que completaste cada paso:

### Entorno
- [ ] Python instalado
- [ ] Jupyter Lab/Notebook instalado
- [ ] Librerías instaladas (duckdb, pandas, openpyxl)

### Estructura
- [ ] Notebook 01 ejecutado → 15 tablas creadas
- [ ] Verifica: `con.query('SELECT COUNT(*) FROM dim_operacion').show()`

### Staging
- [ ] Notebook 02 ejecutado → `stg_aduana` cargada
- [ ] Verifica: `con.query('SELECT COUNT(*) FROM stg_aduana').show()`

### Dimensiones
- [ ] Notebook 03 ejecutado → 12 dimensiones creadas
- [ ] Verifica: cada `dim_*` tiene datos
- [ ] Ejemplo: `con.query('SELECT COUNT(*) FROM dim_pais').show()`

### Fact Table
- [ ] Notebook 04 ejecutado → `fact_aduana_item` creada
- [ ] Verifica: `con.query('SELECT COUNT(*) FROM fact_aduana_item').show()`
- [ ] Verifica: no hay NULLs en claves principales

### Validaciones
- [ ] Notebook 05 ejecutado → todas las pruebas pasaron
- [ ] Verifica: 0 FKs huérfanas
- [ ] Verifica: 0 duplicados

### Power BI
- [ ] Power BI conectado a `aduana.duckdb`
- [ ] Relaciones creadas entre tablas
- [ ] Al menos 3 reportes creados
- [ ] Dashboard guardado

---

## 🆘 Troubleshooting

### Error: "Connection already closed"

**Causa:** ejecutaste `con.close()` y luego intentaste usar `con` de nuevo.

**Solución:** no cierres la conexión hasta que termines todo el notebook.

### Error: "Column not found"

**Causa:** el nombre de la columna no existe (quizás tiene espacios o mayúsculas diferentes).

**Solución:** ejecuta `df.columns` o `con.query('SELECT * FROM tabla LIMIT 1')` para ver los nombres exactos.

### Error: "File already exists"

**Causa:** el archivo `aduana.duckdb` ya existe y no puede sobrescribirse.

**Solución:** borra el archivo antiguo o ejecuta `DROP TABLE IF EXISTS` en tu notebook antes de crear.

### Power BI no se conecta a DuckDB

**Causa:** el driver ODBC no está instalado o mal configurado.

**Solución:** 
1. Intenta instalar el driver: `pip install duckdb-odbc`
2. Si no funciona, usa la opción B (exportar a CSV)

### Los números en la fact table no parecen correctos

**Causa:** hay un problema en el LEFT JOIN o en las conversiones de tipo.

**Solución:** 
1. Ejecuta validaciones (notebook 05)
2. Verifica que cada dimensión tenga los datos esperados
3. Revisa el JOIN en el notebook 04 para asegurar que las claves coinciden

---

## 📚 Conceptos clave resumidos

| Concepto | Explicación |
|----------|-----------|
| **ETL** | Extract (extraer), Transform (transformar), Load (cargar) datos |
| **Data Warehouse** | BD optimizada para análisis, no para operaciones |
| **Bronze/Silver/Gold** | Capas de madurez: crudo, limpio, análisis |
| **Staging** | Tabla de paso donde limpiamos los datos |
| **Dimensión** | Tabla de referencia con datos descriptivos (sin repetir) |
| **Fact Table** | Tabla central con hechos (despachos) + IDs que apuntan a dimensiones |
| **Star Schema** | Diseño: tabla central + dimensiones alrededor |
| **Foreign Key (FK)** | Referencia a un ID en otra tabla |
| **Surrogate Key** | ID artificial que generamos (1, 2, 3...) |
| **Natural Key** | ID del negocio (despacho_cifrado) |
| **LEFT JOIN** | Mantiene todas las filas de la izquierda, aunque no haya match |
| **ROW_NUMBER()** | Función que numera filas (1, 2, 3...) |

---

## 🎯 Próximos pasos

Una vez completado el DWH:

1. **Explora los datos** en Power BI
2. **Crea reportes** más sofisticados (slicers, drill-down)
3. **Automatiza el proceso** (ejecutar ETL cada noche)
4. **Añade más fuentes** de datos
5. **Comparte** el dashboard con stakeholders

---

## 📞 Ayuda y recursos

- **Documentación DuckDB:** https://duckdb.org/docs
- **Documentación Pandas:** https://pandas.pydata.org
- **Documentación Power BI:** https://learn.microsoft.com/power-bi
- **Este proyecto:** https://github.com/RISteven/aduana_bi

---

**Última actualización:** 21 de mayo de 2026

**Creado por:** Equipo de BI Aduanal

**Licencia:** MIT (libre para usar, modificar, compartir)

