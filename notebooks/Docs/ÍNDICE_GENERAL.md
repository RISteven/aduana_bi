# 📚 Índice General — Documentación del DWH Aduana BI

**Bienvenido al Data Warehouse de Aduana. Aquí encontrarás todas las guías para entender y construir tu DW.**

---

## 🎯 ¿Por dónde empiezo?

### Si tienes **30 minutos**
👉 Lee: [QUICK_START_DWH.md](QUICK_START_DWH.md)

Una versión acelerada del proceso. Flujo, fases y comandos clave sin detalles.

### Si tienes **2-3 horas** (RECOMENDADO)
👉 Lee: [PASO_A_PASO_DWH.md](PASO_A_PASO_DWH.md)

La guía completa y humanizada. Explica conceptos, paso a paso detallado, troubleshooting.

### Si quieres **ver diagramas visuales**
👉 Lee: [DIAGRAMAS_DWH.md](DIAGRAMAS_DWH.md)

Visualización del flujo, Star Schema, comparaciones antes/después.

### Si eres **profesor/docente**
👉 Lee: [GUIA_DOCENTE.md](GUIA_DOCENTE.md)

Cómo enseñar el proyecto, secuencia de clases, preguntas para alumnos.

---

## 📖 Documentos disponibles

| Documento | Propósito | Extensión | Público |
|-----------|-----------|-----------|---------|
| [PASO_A_PASO_DWH.md](PASO_A_PASO_DWH.md) | Guía completa y humanizada | 700 líneas | Todos, principiantes |
| [QUICK_START_DWH.md](QUICK_START_DWH.md) | Versión rápida del flujo | 250 líneas | Usuarios con prisa |
| [DIAGRAMAS_DWH.md](DIAGRAMAS_DWH.md) | Visualización de flujos | 500 líneas | Aprendices visuales |
| [GUIA_DOCENTE.md](GUIA_DOCENTE.md) | Método pedagógico | 600 líneas | Profesores |
| **ÍNDICE_GENERAL.md** (este archivo) | Navegación de recursos | 200 líneas | Todos |

---

## 🚀 Flujo de uso típico

### Paso 1: Entender el concepto (30 min)
```
Leer la sección "¿Cuál es el problema?" en PASO_A_PASO_DWH.md
│
└─ ¿Necesitas visuales?
   └─ Mira DIAGRAMAS_DWH.md
```

### Paso 2: Preparar el entorno (15 min)
```
Sección 1 de PASO_A_PASO_DWH.md:
   pip install duckdb pandas openpyxl jupyterlab
```

### Paso 3: Ejecutar los notebooks (2 horas)
```
Sección 3-7 de PASO_A_PASO_DWH.md:
   01_Crear_Estructura_DW.ipynb      (15 min)
   02_Cargar_Staging.ipynb           (20 min)
   03_Cargar_Dimensiones.ipynb       (15 min)
   04_Cargar_Fact_Table.ipynb        (20 min)
   05_Validaciones.ipynb             (10 min)
```

### Paso 4: Conectar a Power BI (30 min)
```
Sección 8 de PASO_A_PASO_DWH.md:
   Instalar ODBC
   Conectar en Power BI
   Crear relaciones
```

### Paso 5: Crear reportes (variable)
```
Exploración libre en Power BI
```

---

## 💡 Decididor rápido

### Quiero entender **qué es** un Data Warehouse
→ [PASO_A_PASO_DWH.md, sección 2](PASO_A_PASO_DWH.md#2-entender-el-problema-y-la-solución)

### Quiero ver **diagramas** de la arquitectura
→ [DIAGRAMAS_DWH.md, sección 4](DIAGRAMAS_DWH.md#4-el-star-schema-esquema-en-estrella)

### Quiero **instrucciones exactas** para ejecutar
→ [PASO_A_PASO_DWH.md, secciones 3-7](PASO_A_PASO_DWH.md#3-crear-la-estructura-de-las-tablas)

### Tengo **error o problema**
→ [PASO_A_PASO_DWH.md, sección troubleshooting](PASO_A_PASO_DWH.md#-troubleshooting)

### Necesito **comandos Python** útiles
→ [QUICK_START_DWH.md, sección de comandos](QUICK_START_DWH.md#comandos-útiles-python)

### Soy **docente** y quiero enseñar esto
→ [GUIA_DOCENTE.md](GUIA_DOCENTE.md)

### Quiero una **cheat sheet**
→ [QUICK_START_DWH.md](QUICK_START_DWH.md)

---

## 🔍 Glosario rápido

| Término | Definición | Dónde aprenderlo |
|---------|-----------|------------------|
| **ETL** | Extraer, Transformar, Cargar | [PASO_A_PASO_DWH.md#conceptos](PASO_A_PASO_DWH.md#-conceptos-clave-resumidos) |
| **Data Warehouse (DW)** | Base de datos para análisis | [PASO_A_PASO_DWH.md#problema](PASO_A_PASO_DWH.md#2-entender-el-problema-y-la-solución) |
| **Bronze/Silver/Gold** | Capas de madurez de datos | [DIAGRAMAS_DWH.md#8](DIAGRAMAS_DWH.md#8-las-4-capas-de-datos) |
| **Star Schema** | Diseño: tabla central + dimensiones | [DIAGRAMAS_DWH.md#4](DIAGRAMAS_DWH.md#4-el-star-schema-esquema-en-estrella) |
| **Staging** | Tabla de paso (datos limpios) | [PASO_A_PASO_DWH.md#4](PASO_A_PASO_DWH.md#4-cargar-y-limpiar-los-datos) |
| **Dimensión (Dim)** | Tabla de referencia (catálogo) | [PASO_A_PASO_DWH.md#5](PASO_A_PASO_DWH.md#5-crear-las-dimensiones) |
| **Fact Table** | Tabla central de hechos (despachos) | [PASO_A_PASO_DWH.md#6](PASO_A_PASO_DWH.md#6-crear-la-tabla-de-hechos) |
| **Foreign Key (FK)** | Relación entre tablas | [DIAGRAMAS_DWH.md#9](DIAGRAMAS_DWH.md#9-relaciones-foreignkeys) |
| **LEFT JOIN** | Unir tablas manteniendo todas las filas | [PASO_A_PASO_DWH.md#6.2](PASO_A_PASO_DWH.md#paso-62-el-código-completo-del-join) |
| **DuckDB** | Base de datos embebida en un archivo | [GUIA_DOCENTE.md](GUIA_DOCENTE.md) |

---

## 📊 Estructura de archivos del proyecto

```
aduana_bi/
├─ 📄 PASO_A_PASO_DWH.md              ⭐ GUÍA PRINCIPAL
├─ 📄 QUICK_START_DWH.md              ⭐ VERSIÓN RÁPIDA
├─ 📄 DIAGRAMAS_DWH.md                ⭐ VISUALES
├─ 📄 GUIA_DOCENTE.md                 (Para profesores)
├─ 📄 ÍNDICE_GENERAL.md               (Este archivo)
│
├─ 📂 notebooks/                      (EJECUTA ESTOS)
│  ├─ 00_Arquitectura_y_Conceptos.ipynb
│  ├─ 01_Crear_Estructura_DW.ipynb
│  ├─ 02_Cargar_Staging.ipynb
│  ├─ 03_Cargar_Dimensiones.ipynb
│  ├─ 04_Cargar_Fact_Table.ipynb
│  └─ 05_Validaciones.ipynb
│
├─ 📂 db/
│  └─ aduana.duckdb                   (SE CREA AUTOMÁTICAMENTE)
│
├─ 📂 data_lake/
│  └─ bronze/
│     └─ DatosCSV.csv                 (DATOS ORIGINALES)
│
├─ 📂 sql/
│  └─ (Scripts Python de soporte)
│
├─ 📂 etl/
│  └─ (Scripts ETL de soporte)
│
└─ 📂 PBI/
   └─ (Aquí creas tu archivo .pbix)
```

---

## ⏱️ Estimación de tiempo

| Actividad | Tiempo | Dificultad |
|-----------|--------|-----------|
| Instalar dependencias | 5 min | ⭐ Fácil |
| Leer PASO_A_PASO_DWH (concepto) | 30 min | ⭐ Fácil |
| Notebook 01 (estructura) | 15 min | ⭐ Fácil |
| Notebook 02 (staging) | 20 min | ⭐ Fácil |
| Notebook 03 (dimensiones) | 15 min | ⭐⭐ Intermedio |
| Notebook 04 (fact table) | 20 min | ⭐⭐⭐ Avanzado |
| Notebook 05 (validaciones) | 10 min | ⭐⭐ Intermedio |
| Conectar Power BI | 15 min | ⭐⭐ Intermedio |
| Crear reportes | 30+ min | Variable |
| **TOTAL** | **2:40 h** | Mixto |

---

## 🛠️ Herramientas necesarias

| Herramienta | Propósito | Versión mín. |
|-------------|----------|-------------|
| **Python** | Lenguaje de programación | 3.9+ |
| **Jupyter** | Ejecutar notebooks | Última |
| **DuckDB** | Base de datos DW | Última |
| **Pandas** | Manipulación de datos | 1.5+ |
| **Power BI Desktop** | Visualización | 2023+ |

**Instalación rápida:**
```bash
pip install jupyterlab duckdb pandas openpyxl
```

---

## ✅ Checklist antes de empezar

- [ ] Python instalado y funcionando
- [ ] Terminal/PowerShell abierta
- [ ] Pasta del proyecto clonada o descargada
- [ ] Dependencias instaladas (`pip install ...`)
- [ ] Editor abierto (VS Code, PyCharm, etc.)
- [ ] Jupyter Lab/Notebook listo para ejecutar

---

## 🎓 Niveles de aprendizaje

### Nivel 1: Principiante
- **Objetivo:** Entender qué es un Data Warehouse
- **Recursos:** 
  - [PASO_A_PASO_DWH.md sección 2](PASO_A_PASO_DWH.md#2-entender-el-problema-y-la-solución)
  - [DIAGRAMAS_DWH.md secciones 1-2](DIAGRAMAS_DWH.md#1-el-flujo-general-de-inicio-a-fin)
- **Tiempo:** 30 min
- **Salida:** Comprensión conceptual

### Nivel 2: Intermedio
- **Objetivo:** Ejecutar el proyecto completo
- **Recursos:** [PASO_A_PASO_DWH.md secciones 1-7](PASO_A_PASO_DWH.md)
- **Tiempo:** 2-3 horas
- **Salida:** DW funcional en DuckDB

### Nivel 3: Avanzado
- **Objetivo:** Modificar el modelo, agregar datos, optimizar
- **Recursos:** [GUIA_DOCENTE.md](GUIA_DOCENTE.md), comentarios en notebooks
- **Tiempo:** 4+ horas
- **Salida:** DW personalizado y escalable

### Nivel 4: Experto
- **Objetivo:** Automatizar, produccionizar, enseñar
- **Recursos:** Código fuente, documentación técnica
- **Tiempo:** Variable
- **Salida:** Sistema de BI completo

---

## 🔗 Enlaces útiles

### Documentación oficial
- [DuckDB Docs](https://duckdb.org/docs/)
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/)
- [Power BI Learning](https://learn.microsoft.com/power-bi/)
- [SQL Tutorial](https://www.w3schools.com/sql/)

### Repositorio
- [GitHub: aduana_bi](https://github.com/RISteven/aduana_bi)

### Este proyecto
- [PASO_A_PASO_DWH.md](PASO_A_PASO_DWH.md) - Guía principal
- [QUICK_START_DWH.md](QUICK_START_DWH.md) - Versión acelerada
- [DIAGRAMAS_DWH.md](DIAGRAMAS_DWH.md) - Visual

---

## ❓ Preguntas frecuentes

### P: ¿Por dónde empiezo si nunca he hecho un DW?
**R:** Lee [PASO_A_PASO_DWH.md](PASO_A_PASO_DWH.md) de inicio a fin. Toma 2-3 horas pero vale la pena.

### P: ¿Tengo que entender SQL para esto?
**R:** No, pero ayuda. Los notebooks tienen SQL comentado. Aprenderás mientras lo ejecutas.

### P: ¿Puedo modificar los datos o agregar más tablas?
**R:** Sí, totalmente. El proyecto está diseñado para ser extensible. Ver GUIA_DOCENTE.md para ideas.

### P: ¿Funciona en Windows/Mac/Linux?
**R:** Sí, Python y DuckDB funcionan en los tres. Power BI solo en Windows/Web.

### P: ¿Cuánto espacio ocupa?
**R:** El archivo `aduana.duckdb` ocupa ~20-50 MB. Los CSVs originales dependen del tamaño.

### P: ¿Puedo usar esto en producción?
**R:** Con ajustes sí. Ver GUIA_DOCENTE.md para escalado y automatización.

---

## 📝 Versión y metadata

| Propiedad | Valor |
|-----------|-------|
| **Proyecto** | Aduana BI Data Warehouse |
| **Versión** | 1.0 |
| **Última actualización** | 21 de mayo de 2026 |
| **Creador** | Equipo de BI Aduanal |
| **Licencia** | MIT |
| **Status** | Completo y funcional |

---

## 🎯 Próximos pasos después de completar

1. **Explore los datos** en Power BI con consultas ad-hoc
2. **Cree dashboards** más sofisticados (slicers, drill-down, custom metrics)
3. **Automatice** el ETL (scheduler, CI/CD)
4. **Agregue más fuentes** de datos
5. **Comparta** el dashboard con stakeholders
6. **Monitoree** la calidad de datos (data quality checks)
7. **Escale** a más usuarios (Power BI Service)

---

**¿Listo para empezar? 👉 [Abre PASO_A_PASO_DWH.md](PASO_A_PASO_DWH.md)**

