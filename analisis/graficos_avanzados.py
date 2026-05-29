"""
==============================================================================
ANÁLISIS AVANZADO DE DATOS ADUANEROS – 30 VISUALIZACIONES
Comercio Exterior de Paraguay
==============================================================================
Este script genera 30 gráficos para enseñar análisis de comercio exterior.
Combina datos reales (archivo Silver de febrero 2026, 50 registros) con datos
simulados para los análisis que requieren series temporales o catálogos más
amplios. Los gráficos con datos simulados lo indican claramente en su título.

Librerías necesarias:
  pip install duckdb pandas numpy matplotlib seaborn

Para ejecutar:
  python analisis/graficos_avanzados.py
==============================================================================
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 1 – IMPORTAR LIBRERÍAS
# Cada librería cumple un rol específico en el análisis
# ─────────────────────────────────────────────────────────────────────────────
import duckdb          # Motor SQL para leer archivos Parquet
import numpy as np     # Operaciones matemáticas y generación de datos simulados
import pandas as pd    # Manipulación de tablas de datos
import matplotlib.pyplot as plt              # Gráficos base
import matplotlib.ticker as mticker         # Formateo de ejes
import matplotlib.patches as mpatches       # Figuras geométricas en gráficos
import matplotlib.cm as cm                  # Mapas de color
import seaborn as sns                       # Heatmaps y gráficos estadísticos
from pathlib import Path                    # Rutas de archivo portátiles

# Fijamos la semilla aleatoria para que los datos simulados sean reproducibles
np.random.seed(42)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 2 – RUTAS DE ARCHIVOS
# Path(__file__) = ubicación de este script
# .parent        = sube una carpeta
# ─────────────────────────────────────────────────────────────────────────────
CARPETA_PROYECTO = Path(__file__).parent.parent
ARCHIVO_PARQUET  = CARPETA_PROYECTO / "data_lake" / "silver" / "aduana_item_clean.parquet"
CARPETA_SALIDA   = Path(__file__).parent / "graficos" / "avanzados"
CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 3 – CARGAR Y PREPARAR LOS DATOS REALES
# ─────────────────────────────────────────────────────────────────────────────
conexion     = duckdb.connect()
datos        = conexion.execute(f"SELECT * FROM '{ARCHIVO_PARQUET}'").fetchdf()

# Las columnas de tributos llegaron como texto → convertir a número
columnas_tributos = ["DERECHO", "IVA", "ISC", "RENTA", "OTROS", "TOTAL", "SERVICIO", "COTIZACION"]
for col in columnas_tributos:
    datos[col] = pd.to_numeric(datos[col], errors="coerce")

# Columnas calculadas
datos["DIAS_DESPACHO"]  = (datos["CANCELACION"] - datos["OFICIALIZACION"]).dt.days
datos["PRECIO_USD_KG"]  = datos["FOB DOLAR"] / datos["KILO NETO"].replace(0, np.nan)
datos["RATIO_FLETE"]    = datos["FLETE DOLAR"] / datos["FOB DOLAR"].replace(0, np.nan)
datos["TRIBUTOS_TOTAL"] = datos[["DERECHO", "IVA", "ISC", "RENTA", "OTROS"]].sum(axis=1)

# Subconjuntos por tipo de operación
exp = datos[datos["OPERACION"] == "EXPORTACION"].copy()
imp = datos[datos["OPERACION"] == "IMPORTACION"].copy()

print(f"✔ Datos cargados: {len(datos)} registros  "
      f"(Exportaciones: {len(exp)} | Importaciones: {len(imp)})")


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN 4 – COLORES Y ESTILO GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
VERDE   = "#016948"   # Exportaciones
ROJO    = "#B44365"   # Importaciones
AZUL    = "#012169"   # Análisis generales
NARANJA = "#E8A838"   # Advertencias / simulados

PALETA = ["#012169", "#D4285B", "#009EFF", "#259B9A",
          "#6CACE4", "#7B2A8D", "#E8A838", "#4A4A4A",
          "#2E8B57", "#DC143C", "#4B0082", "#AAAAAA"]

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "figure.dpi":        120,
    "axes.titlesize":    11,
    "axes.labelsize":    9,
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
    "legend.fontsize":   8,
})

def guardar(nombre: str) -> None:
    """Guarda el gráfico activo en la carpeta de salida y lo cierra."""
    ruta = CARPETA_SALIDA / nombre
    plt.savefig(ruta, bbox_inches="tight")
    plt.close("all")
    print(f"  ✔  {ruta.name}")

def nota_simulado(eje, texto="Datos simulados con fines pedagógicos"):
    """Agrega una nota de pie al gráfico cuando los datos son sintéticos."""
    eje.annotate(
        f"⚠ {texto}",
        xy=(0.01, -0.12), xycoords="axes fraction",
        fontsize=7, color="#888888", style="italic"
    )


# ===========================================================================
# GRÁFICO 01 – VARIACIÓN INTERANUAL DE EXPORTACIONES
# ¿Qué enseña? Comparar el desempeño exportador año a año.
# ¿Por qué es útil? Identifica tendencias, shocks (p. ej. pandemia) y recuperaciones.
# Datos: SIMULADOS basados en tendencias del comercio exterior de Paraguay.
# ===========================================================================
print("\n[G01] Variación interanual de exportaciones")

anios_historicos         = [2020, 2021, 2022, 2023, 2024, 2025, 2026]
monto_exportado_millones = [5100, 6400, 8900, 7200, 8500, 9100, 9800]

# Variación porcentual: (año_actual - año_anterior) / año_anterior × 100
variacion_pct = [None] + [
    (monto_exportado_millones[i] - monto_exportado_millones[i - 1])
    / monto_exportado_millones[i - 1] * 100
    for i in range(1, len(monto_exportado_millones))
]

fig, (ax_monto, ax_var) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Variación Interanual de Exportaciones (2020–2026)\n[Datos simulados]",
             fontsize=12, fontweight="bold")

# Panel izquierdo: monto total
ax_monto.plot(anios_historicos, monto_exportado_millones, marker="o",
              color=VERDE, linewidth=2.5, markersize=8, zorder=3)
ax_monto.fill_between(anios_historicos, monto_exportado_millones, alpha=0.15, color=VERDE)
for x, y in zip(anios_historicos, monto_exportado_millones):
    ax_monto.text(x, y + 120, f"${y:,.0f}M", ha="center", fontsize=7.5, color="#333")
ax_monto.axvspan(2019.6, 2020.4, alpha=0.08, color="red", label="Pandemia COVID-19")
ax_monto.text(2020, 4600, "COVID-19", ha="center", fontsize=7.5, color="red")
ax_monto.set_xlabel("Año")
ax_monto.set_ylabel("USD Millones")
ax_monto.set_title("Monto total exportado por año")
ax_monto.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax_monto)

# Panel derecho: variación porcentual (barras en verde/rojo según signo)
anios_var  = anios_historicos[1:]
valores_var = variacion_pct[1:]
colores_var = [VERDE if v >= 0 else ROJO for v in valores_var]
barras = ax_var.bar(anios_var, valores_var, color=colores_var, edgecolor="white", width=0.6)
for b, v in zip(barras, valores_var):
    despl = 0.5 if v >= 0 else -1.8
    ax_var.text(b.get_x() + b.get_width() / 2, v + despl, f"{v:+.1f}%", ha="center", fontsize=8)
ax_var.axhline(0, color="#555", linewidth=0.9)
ax_var.set_xlabel("Año")
ax_var.set_ylabel("Variación (%)")
ax_var.set_title("Variación porcentual respecto al año anterior")
ax_var.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax_var)

plt.tight_layout()
guardar("G01_variacion_interanual.png")


# ===========================================================================
# GRÁFICO 02 – TOP 10 PRODUCTOS IMPORTADOS
# ¿Qué enseña? Identificar los rubros que más ingresaron al país por valor FOB.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G02] Top 10 productos importados")

fob_importaciones = (
    imp.groupby("RUBRO")["FOB DOLAR"]
    .sum()
    .sort_values(ascending=True)
    .tail(10)
)
etiquetas = [r[:40] + "…" if len(r) > 40 else r for r in fob_importaciones.index]

fig, ax = plt.subplots(figsize=(11, 6))
fig.suptitle("Top Productos Importados por Valor FOB (Feb 2026)", fontsize=12, fontweight="bold")

barras = ax.barh(etiquetas, fob_importaciones.values,
                 color=PALETA[:len(fob_importaciones)], edgecolor="white", height=0.65)
for b in barras:
    ancho = b.get_width()
    ax.text(ancho + ancho * 0.02, b.get_y() + b.get_height() / 2,
            f"${ancho:,.0f}", va="center", fontsize=8)

ax.set_xlabel("FOB (USD)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e3:.0f}K"))
ax.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G02_top10_productos_importados.png")


# ===========================================================================
# GRÁFICO 03 – PARTICIPACIÓN DE PAÍSES EN EXPORTACIÓN
# ¿Qué enseña? Ver a qué países se exporta y en qué proporción.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G03] Participación de países en exportación")

fob_por_pais_exp = (
    exp.groupby("PAIS_DEST_DESC")["FOB DOLAR"]
    .sum()
    .sort_values(ascending=False)
)

# Agrupamos países pequeños en "Otros" si no son top 6
top_n          = 6
top_paises     = fob_por_pais_exp.head(top_n)
resto          = fob_por_pais_exp.iloc[top_n:].sum()
if resto > 0:
    top_paises = pd.concat([top_paises, pd.Series({"Otros": resto})])

fig, ax = plt.subplots(figsize=(8, 6))
fig.suptitle("Participación de Países en Exportaciones (Feb 2026)\nValor FOB USD",
             fontsize=12, fontweight="bold")

cuñas, textos, porcentajes = ax.pie(
    top_paises.values,
    labels=top_paises.index,
    autopct="%1.1f%%",
    colors=PALETA[:len(top_paises)],
    startangle=90,
    wedgeprops={"edgecolor": "white", "linewidth": 1.8},
    pctdistance=0.75,
)
for pct in porcentajes:
    pct.set_fontsize(9)
    pct.set_fontweight("bold")
    pct.set_color("white")

total_exp = fob_por_pais_exp.sum()
ax.text(0, -1.35, f"Total exportado: ${total_exp:,.0f} USD",
        ha="center", fontsize=9, color="#444")

plt.tight_layout()
guardar("G03_participacion_paises_exportacion.png")


# ===========================================================================
# GRÁFICO 04 – CRECIMIENTO DE RUBROS CLAVE
# ¿Qué enseña? Ver la evolución mensual de los principales rubros.
# Datos: SIMULADOS (serie mensual 12 meses).
# ===========================================================================
print("[G04] Crecimiento de rubros clave")

meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
         "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
rubros_clave = {
    "Oleaginosas":  [120, 135, 180, 200, 175, 140, 110, 100, 115, 130, 145, 125],
    "Textiles":     [ 80,  95, 105, 110,  98,  90,  85,  92, 100, 108, 115,  88],
    "Químicos":     [ 60,  55,  70,  75,  80,  85,  78,  72,  68,  74,  80,  65],
    "Combustibles": [ 50,  45,  60,  65,  70,  68,  62,  58,  55,  60,  65,  55],
}

fig, ax = plt.subplots(figsize=(12, 5))
fig.suptitle("Evolución Mensual de Rubros Clave – Exportaciones (2025)\n[Datos simulados]",
             fontsize=12, fontweight="bold")

for (nombre_rubro, valores), color in zip(rubros_clave.items(), PALETA):
    ax.plot(meses, valores, marker="o", label=nombre_rubro, color=color,
            linewidth=2, markersize=5)

ax.set_ylabel("FOB (USD miles)")
ax.set_xlabel("Mes")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax)

plt.tight_layout()
guardar("G04_crecimiento_rubros_clave.png")


# ===========================================================================
# GRÁFICO 05 – ANÁLISIS DE ESTACIONALIDAD
# ¿Qué enseña? Identificar en qué meses el comercio exterior es más intenso.
# Los colores más oscuros indican mayor valor exportado.
# Datos: SIMULADOS (patrón estacional agrícola de Paraguay).
# ===========================================================================
print("[G05] Análisis de estacionalidad")

anios_heatmap = [2022, 2023, 2024, 2025]
base_mensual  = np.array([90, 100, 130, 150, 140, 110, 95, 88, 95, 105, 115, 95])

# Generamos una matriz año × mes con ligera variación aleatoria
matriz_calor = np.array([
    base_mensual * (1 + 0.05 * (i - 1) + np.random.uniform(-0.08, 0.08, 12))
    for i in range(len(anios_heatmap))
])

fig, ax = plt.subplots(figsize=(13, 4))
fig.suptitle("Estacionalidad de Exportaciones – FOB Mensual (USD millones)\n[Datos simulados]",
             fontsize=12, fontweight="bold")

im = ax.imshow(matriz_calor, cmap="YlGn", aspect="auto")
ax.set_xticks(range(12))
ax.set_xticklabels(meses)
ax.set_yticks(range(len(anios_heatmap)))
ax.set_yticklabels(anios_heatmap)
ax.set_xlabel("Mes")
ax.set_ylabel("Año")

for fila in range(len(anios_heatmap)):
    for col in range(12):
        valor = matriz_calor[fila, col]
        color_texto = "white" if valor > matriz_calor.max() * 0.65 else "black"
        ax.text(col, fila, f"{valor:.0f}", ha="center", va="center",
                fontsize=7.5, color=color_texto)

fig.colorbar(im, ax=ax, label="FOB (USD millones)")
nota_simulado(ax)

plt.tight_layout()
guardar("G05_estacionalidad.png")


# ===========================================================================
# GRÁFICO 06 – DISTRIBUCIÓN GEOGRÁFICA (BURBUJA POR PAÍS)
# ¿Qué enseña? Ver el peso de cada país destino según FOB y cantidad de ítems.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G06] Distribución geográfica")

geo = (
    datos.groupby(["PAIS_DEST_DESC", "OPERACION"])
    .agg(fob_total=("FOB DOLAR", "sum"), items=("FOB DOLAR", "count"))
    .reset_index()
)

fig, ax = plt.subplots(figsize=(11, 6))
fig.suptitle("Distribución por País – FOB Total y Cantidad de Ítems (Feb 2026)",
             fontsize=12, fontweight="bold")

for operacion, color, marcador in [("EXPORTACION", VERDE, "o"), ("IMPORTACION", ROJO, "s")]:
    subset = geo[geo["OPERACION"] == operacion]
    scatter = ax.scatter(
        range(len(subset)),
        subset["fob_total"],
        s=subset["items"] * 120,        # tamaño = cantidad de ítems
        color=color,
        alpha=0.7,
        marker=marcador,
        edgecolors="white",
        linewidths=1.2,
        label=operacion,
        zorder=3,
    )
    for idx, (_, fila) in enumerate(subset.iterrows()):
        ax.text(idx, fila["fob_total"] + fila["fob_total"] * 0.04,
                fila["PAIS_DEST_DESC"][:12], ha="center", fontsize=7, rotation=25)

ax.set_ylabel("FOB (USD)")
ax.set_xlabel("País (por operación)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e3:.0f}K"))
ax.set_xticks([])
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.4)

leyenda_tam = [
    plt.scatter([], [], s=120, color="#999", label="1 ítem"),
    plt.scatter([], [], s=240, color="#999", label="2 ítems"),
    plt.scatter([], [], s=480, color="#999", label="4 ítems"),
]
ax.legend(handles=ax.get_legend_handles_labels()[0] + leyenda_tam,
          labels=ax.get_legend_handles_labels()[1] + ["1 ítem", "2 ítems", "4 ítems"],
          fontsize=7.5, loc="upper right")

plt.tight_layout()
guardar("G06_distribucion_geografica.png")


# ===========================================================================
# GRÁFICO 07 – ANÁLISIS DE RENTABILIDAD POR PRODUCTO
# ¿Qué enseña? Comparar productos según su precio unitario (USD/kg) y volumen.
# Más precio por kilo = mayor valor agregado del producto.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G07] Análisis de rentabilidad por producto")

datos_validos = datos[datos["PRECIO_USD_KG"].notna() & (datos["PRECIO_USD_KG"] < 500)].copy()

fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle("Rentabilidad por Producto: Precio USD/kg vs Volumen (Feb 2026)",
             fontsize=12, fontweight="bold")

for operacion, color in [("EXPORTACION", VERDE), ("IMPORTACION", ROJO)]:
    subset = datos_validos[datos_validos["OPERACION"] == operacion]
    ax.scatter(subset["KILO NETO"], subset["PRECIO_USD_KG"],
               color=color, alpha=0.75, s=70, edgecolors="white",
               linewidths=0.8, label=operacion, zorder=3)

ax.set_xlabel("Kilo Neto (kg)")
ax.set_ylabel("Precio unitario (USD/kg)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e3:.0f}K"))
ax.legend()
ax.grid(linestyle="--", alpha=0.35)

umbral_alto = datos_validos["PRECIO_USD_KG"].quantile(0.75)
ax.axhline(umbral_alto, color=NARANJA, linestyle="--", linewidth=1, alpha=0.7)
ax.text(ax.get_xlim()[1] * 0.02, umbral_alto + 1,
        f"Percentil 75 (${umbral_alto:.1f}/kg)", fontsize=7.5, color=NARANJA)

plt.tight_layout()
guardar("G07_rentabilidad_por_producto.png")


# ===========================================================================
# GRÁFICO 08 – COMPARATIVA IMPORTACIÓN / EXPORTACIÓN
# ¿Qué enseña? Comparar ambas operaciones en varias métricas clave.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G08] Comparativa importación/exportación")

metricas = {
    "FOB Total\n(USD miles)":  [exp["FOB DOLAR"].sum() / 1e3, imp["FOB DOLAR"].sum() / 1e3],
    "Kilos\n(miles)":          [exp["KILO NETO"].sum() / 1e3, imp["KILO NETO"].sum() / 1e3],
    "Ítems":                   [len(exp),                      len(imp)],
    "Tributos\n(USD)":         [exp["TRIBUTOS_TOTAL"].sum(),   imp["TRIBUTOS_TOTAL"].sum()],
    "Días despacho\n(prom.)":  [exp["DIAS_DESPACHO"].mean(),   imp["DIAS_DESPACHO"].mean()],
}
etiquetas_metricas = list(metricas.keys())
valores_exp = [v[0] for v in metricas.values()]
valores_imp = [v[1] for v in metricas.values()]

posiciones = np.arange(len(etiquetas_metricas))
ancho      = 0.35

fig, ax = plt.subplots(figsize=(12, 5))
fig.suptitle("Comparativa de Métricas: Exportación vs Importación (Feb 2026)",
             fontsize=12, fontweight="bold")

b_exp = ax.bar(posiciones - ancho / 2, valores_exp, ancho, label="Exportación",
               color=VERDE, edgecolor="white", alpha=0.9)
b_imp = ax.bar(posiciones + ancho / 2, valores_imp, ancho, label="Importación",
               color=ROJO, edgecolor="white", alpha=0.9)

for b in list(b_exp) + list(b_imp):
    h = b.get_height()
    ax.text(b.get_x() + b.get_width() / 2, h + h * 0.03,
            f"{h:,.1f}", ha="center", fontsize=7.5)

ax.set_xticks(posiciones)
ax.set_xticklabels(etiquetas_metricas, fontsize=8.5)
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G08_comparativa_imp_exp.png")


# ===========================================================================
# GRÁFICO 09 – EVOLUCIÓN DE PRECIOS FOB
# ¿Qué enseña? Cómo varía el precio promedio de exportación mes a mes.
# Un precio creciente puede indicar mejor calidad o mejora en productos.
# Datos: SIMULADOS (tendencia mensual 2025).
# ===========================================================================
print("[G09] Evolución de precios FOB")

precio_promedio_mensual = [28, 31, 35, 38, 36, 33, 30, 29, 31, 34, 36, 38]  # USD miles

fig, ax = plt.subplots(figsize=(11, 5))
fig.suptitle("Evolución del Precio FOB Promedio por Despacho (2025)\n[Datos simulados]",
             fontsize=12, fontweight="bold")

ax.plot(meses, precio_promedio_mensual, marker="o", color=AZUL,
        linewidth=2.5, markersize=7, zorder=3)
ax.fill_between(meses, precio_promedio_mensual, alpha=0.12, color=AZUL)
for x, y in zip(meses, precio_promedio_mensual):
    ax.text(x, y + 0.5, f"${y}K", ha="center", fontsize=7.5, color="#333")

promedio_anual = np.mean(precio_promedio_mensual)
ax.axhline(promedio_anual, color=NARANJA, linestyle="--", linewidth=1.5, alpha=0.8)
ax.text(0, promedio_anual + 0.4, f"Prom. anual ${promedio_anual:.0f}K",
        fontsize=7.5, color=NARANJA)

ax.set_xlabel("Mes")
ax.set_ylabel("FOB promedio (USD miles)")
ax.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax)

plt.tight_layout()
guardar("G09_evolucion_precios_fob.png")


# ===========================================================================
# GRÁFICO 10 – CONTRIBUCIÓN DE PRINCIPALES CLIENTES (PARETO)
# ¿Qué enseña? El principio de Pareto (80/20): pocos países concentran
# la mayoría del valor exportado. Útil para priorizar relaciones comerciales.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G10] Contribución de principales clientes (Pareto)")

fob_clientes = datos.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum().sort_values(ascending=False)
total_fob    = fob_clientes.sum()
acumulado    = (fob_clientes.cumsum() / total_fob * 100)

fig, ax1 = plt.subplots(figsize=(11, 5))
fig.suptitle("Análisis de Pareto – Contribución de Países por FOB (Feb 2026)",
             fontsize=12, fontweight="bold")

ax2 = ax1.twinx()   # eje derecho para el porcentaje acumulado

barras = ax1.bar(fob_clientes.index, fob_clientes.values,
                 color=PALETA[:len(fob_clientes)], edgecolor="white", width=0.7)
ax2.plot(fob_clientes.index, acumulado.values, marker="D", color=NARANJA,
         linewidth=2.5, markersize=6, zorder=5, label="Acumulado")

ax2.axhline(80, color="#aaa", linestyle="--", linewidth=1)
ax2.text(len(fob_clientes) - 0.5, 81, "80%", fontsize=8, color="#aaa", ha="right")

ax1.set_xlabel("País")
ax1.set_ylabel("FOB (USD)")
ax2.set_ylabel("% Acumulado")
ax2.set_ylim(0, 110)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e3:.0f}K"))
ax1.tick_params(axis="x", rotation=30)
ax2.legend(loc="center right")
ax1.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G10_pareto_clientes.png")


# ===========================================================================
# GRÁFICO 11 – TIEMPOS DE DESPACHO PROMEDIO
# ¿Qué enseña? Cuántos días tarda un despacho en procesarse según su tipo.
# Una aduana eficiente debería tener tiempos bajos y consistentes.
# Datos: REALES (diferencia en días entre OFICIALIZACION y CANCELACION).
# ===========================================================================
print("[G11] Tiempos de despacho promedio")

tiempos_exp = exp["DIAS_DESPACHO"].dropna()
tiempos_imp = imp["DIAS_DESPACHO"].dropna()

fig, (ax_box, ax_dist) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Tiempos de Despacho: Exportación vs Importación (Feb 2026)",
             fontsize=12, fontweight="bold")

# Panel izquierdo: diagrama de caja
bp = ax_box.boxplot(
    [tiempos_exp, tiempos_imp],
    tick_labels=["Exportación", "Importación"],
    patch_artist=True,
    medianprops={"color": "white", "linewidth": 2},
    boxprops={"linewidth": 1.5},
    whiskerprops={"linewidth": 1.2},
    flierprops={"marker": "o", "markersize": 5, "alpha": 0.5},
)
for parche, color in zip(bp["boxes"], [VERDE, ROJO]):
    parche.set_facecolor(color)
    parche.set_alpha(0.75)
ax_box.set_ylabel("Días")
ax_box.set_title("Dispersión de tiempos")
ax_box.grid(axis="y", linestyle="--", alpha=0.4)

# Panel derecho: histograma superpuesto
ax_dist.hist(tiempos_exp, bins=8, color=VERDE, alpha=0.65, label="Exportación", edgecolor="white")
ax_dist.hist(tiempos_imp, bins=8, color=ROJO,  alpha=0.65, label="Importación", edgecolor="white")
prom_exp = tiempos_exp.mean()
prom_imp = tiempos_imp.mean()
ax_dist.axvline(prom_exp, color=VERDE, linestyle="--", linewidth=1.5,
                label=f"Prom. exp: {prom_exp:.1f}d")
ax_dist.axvline(prom_imp, color=ROJO,  linestyle="--", linewidth=1.5,
                label=f"Prom. imp: {prom_imp:.1f}d")
ax_dist.set_xlabel("Días de despacho")
ax_dist.set_ylabel("Frecuencia")
ax_dist.set_title("Distribución de tiempos")
ax_dist.legend()
ax_dist.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G11_tiempos_despacho.png")


# ===========================================================================
# GRÁFICO 12 – ANÁLISIS DE CONCENTRACIÓN DE MERCADO (CURVA DE LORENZ)
# ¿Qué enseña? Cuánto del valor exportado se concentra en pocos países.
# La curva de Lorenz muestra la desigualdad: cuanto más curva, más concentrado.
# El coeficiente de Gini mide esa concentración (0 = perfecto, 1 = total concentración).
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G12] Análisis de concentración de mercado (Lorenz + Gini)")

fob_paises_sorted = datos.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum().sort_values()
n_paises          = len(fob_paises_sorted)
fob_acum          = fob_paises_sorted.cumsum() / fob_paises_sorted.sum()
paises_acum       = np.arange(1, n_paises + 1) / n_paises

# Coeficiente de Gini = 1 - 2 * área bajo la curva de Lorenz
gini = 1 - 2 * np.trapezoid(fob_acum, paises_acum)

fig, ax = plt.subplots(figsize=(7, 6))
fig.suptitle("Curva de Lorenz – Concentración de Mercado (Feb 2026)",
             fontsize=12, fontweight="bold")

ax.plot([0] + list(paises_acum), [0] + list(fob_acum),
        color=AZUL, linewidth=2.5, label=f"Lorenz real (Gini = {gini:.2f})")
ax.plot([0, 1], [0, 1], color="#aaa", linestyle="--", linewidth=1.5, label="Distribución perfecta")
ax.fill_between([0] + list(paises_acum), [0] + list(fob_acum), [0] + list(paises_acum),
                alpha=0.15, color=AZUL, label="Área de concentración")

ax.set_xlabel("% acumulado de países")
ax.set_ylabel("% acumulado de FOB")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v*100:.0f}%"))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v*100:.0f}%"))
ax.legend()
ax.grid(linestyle="--", alpha=0.4)
ax.text(0.05, 0.85, f"Gini = {gini:.2f}\n{'Alta concentración' if gini > 0.5 else 'Concentración moderada'}",
        transform=ax.transAxes, fontsize=9, bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

plt.tight_layout()
guardar("G12_lorenz_concentracion.png")


# ===========================================================================
# GRÁFICO 13 – IDENTIFICACIÓN DE PRODUCTOS EMERGENTES
# ¿Qué enseña? Detectar productos con alta tasa de crecimiento y buen volumen.
# Cuadrante ideal: alto crecimiento + alta participación → productos estrella.
# Datos: SIMULADOS.
# ===========================================================================
print("[G13] Identificación de productos emergentes")

productos_emergentes = {
    "Canola":           {"participacion": 8,  "crecimiento": 45, "fob": 120},
    "Chia":             {"participacion": 3,  "crecimiento": 80, "fob":  60},
    "Soja orgánica":    {"participacion": 12, "crecimiento": 30, "fob": 180},
    "Carne bovina":     {"participacion": 18, "crecimiento": 15, "fob": 250},
    "Madera procesada": {"participacion": 7,  "crecimiento": 22, "fob":  90},
    "Textiles técnicos":{"participacion": 5,  "crecimiento": 55, "fob":  80},
    "Aceite de girasol":{"participacion": 10, "crecimiento": 10, "fob": 140},
    "Maíz especial":    {"participacion": 15, "crecimiento":  5, "fob": 200},
    "Moringa":          {"participacion": 2,  "crecimiento": 95, "fob":  40},
    "Yerba mate":       {"participacion": 6,  "crecimiento": 28, "fob": 100},
}

fig, ax = plt.subplots(figsize=(10, 7))
fig.suptitle("Matriz de Productos Emergentes: Participación vs Crecimiento\n[Datos simulados]",
             fontsize=12, fontweight="bold")

for producto, datos_prod in productos_emergentes.items():
    ax.scatter(datos_prod["participacion"], datos_prod["crecimiento"],
               s=datos_prod["fob"] * 1.5, color=AZUL, alpha=0.65,
               edgecolors="white", linewidths=1.2)
    ax.text(datos_prod["participacion"] + 0.3, datos_prod["crecimiento"] + 1,
            producto, fontsize=7.5, color="#333")

prom_part = np.mean([d["participacion"] for d in productos_emergentes.values()])
prom_crec = np.mean([d["crecimiento"]   for d in productos_emergentes.values()])
ax.axvline(prom_part, color="#aaa", linestyle="--", linewidth=1)
ax.axhline(prom_crec, color="#aaa", linestyle="--", linewidth=1)

ax.text(prom_part + 0.2, ax.get_ylim()[1] * 0.97, "Cuota promedio", fontsize=7, color="#999")
ax.text(ax.get_xlim()[0] + 0.1, prom_crec + 1, "Crecimiento promedio", fontsize=7, color="#999")

ax.set_xlabel("Participación de mercado (%)")
ax.set_ylabel("Tasa de crecimiento (%)")
ax.grid(linestyle="--", alpha=0.35)
nota_simulado(ax)

plt.tight_layout()
guardar("G13_productos_emergentes.png")


# ===========================================================================
# GRÁFICO 14 – IMPACTO DE REGULACIONES ARANCELARIAS
# ¿Qué enseña? Comparar la carga tributaria según el régimen aduanero.
# Algunos regímenes (maquila, temporaria) tienen arancel reducido o cero.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G14] Impacto de regulaciones arancelarias")

tributos_por_regimen = (
    datos.groupby("REGIMEN")[["DERECHO", "IVA", "ISC", "RENTA", "OTROS"]]
    .sum()
)
tributos_por_regimen.index = [r[:35] + "…" if len(r) > 35 else r for r in tributos_por_regimen.index]
tributos_por_regimen = tributos_por_regimen[tributos_por_regimen.sum(axis=1) > 0]

fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Carga Tributaria por Régimen Aduanero (Feb 2026)", fontsize=12, fontweight="bold")

if not tributos_por_regimen.empty:
    tributos_por_regimen.plot(kind="barh", ax=ax, stacked=True,
                              color=PALETA[:5], edgecolor="white")
    ax.set_xlabel("Monto en tributos (Gs)")
    ax.legend(title="Tributo", loc="lower right")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
else:
    ax.text(0.5, 0.5, "Sin datos tributarios en este período",
            ha="center", va="center", transform=ax.transAxes, fontsize=12, color="#666")
    ax.set_visible(False)

    # Usar datos simulados de referencia
    regimenes_sim = ["Importación a Consumo", "Importación Temporaria", "Exportación a Consumo", "Maquila"]
    tributos_sim  = {
        "Derecho": [45000, 5000,  0, 0],
        "IVA":     [80000, 8000,  0, 0],
        "ISC":     [12000, 0,     0, 0],
        "Renta":   [15000, 2000,  0, 0],
    }
    fig2, ax = plt.subplots(figsize=(12, 5))
    base = np.zeros(4)
    for (trib, vals), color in zip(tributos_sim.items(), PALETA[:4]):
        ax.barh(regimenes_sim, vals, left=base, label=trib, color=color, edgecolor="white")
        base += np.array(vals)
    ax.set_xlabel("Monto en tributos (Gs)")
    ax.legend(title="Tributo")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    nota_simulado(ax)
    fig.suptitle("Carga Tributaria por Régimen Aduanero\n[Datos simulados]",
                 fontsize=12, fontweight="bold")

plt.tight_layout()
guardar("G14_impacto_aranceles.png")


# ===========================================================================
# GRÁFICO 15 – VOLATILIDAD DE VOLÚMENES POR RUBRO
# ¿Qué enseña? Cuánto varían los volúmenes dentro de un mismo rubro.
# Alta dispersión → mucha irregularidad en las exportaciones de ese rubro.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G15] Volatilidad de volúmenes por rubro")

vol_por_rubro = datos[datos["KILO NETO"] > 0].copy()
rubros_frecuentes = (
    vol_por_rubro.groupby("RUBRO")["KILO NETO"]
    .count()
    .nlargest(6)
    .index
)
vol_filtrado = vol_por_rubro[vol_por_rubro["RUBRO"].isin(rubros_frecuentes)]
etiq = {r: (r[:25] + "…" if len(r) > 25 else r) for r in rubros_frecuentes}
vol_filtrado = vol_filtrado.copy()
vol_filtrado["RUBRO_CORTO"] = vol_filtrado["RUBRO"].map(etiq)

fig, ax = plt.subplots(figsize=(12, 6))
fig.suptitle("Volatilidad de Volúmenes (Kilo Neto) por Rubro (Feb 2026)",
             fontsize=12, fontweight="bold")

datos_boxplot = [vol_filtrado[vol_filtrado["RUBRO"] == r]["KILO NETO"].values
                 for r in rubros_frecuentes]
etiquetas_bp  = [etiq[r] for r in rubros_frecuentes]

bp = ax.boxplot(datos_boxplot, tick_labels=etiquetas_bp, patch_artist=True,
                medianprops={"color": "white", "linewidth": 2},
                flierprops={"marker": "o", "markersize": 5, "alpha": 0.5})
for parche, color in zip(bp["boxes"], PALETA):
    parche.set_facecolor(color)
    parche.set_alpha(0.75)

ax.set_ylabel("Kilo Neto (kg)")
ax.tick_params(axis="x", rotation=30, labelsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v/1e3:.0f}K"))
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G15_volatilidad_volumenes.png")


# ===========================================================================
# GRÁFICO 16 – RANKING DE DESTINOS POR FOB
# ¿Qué enseña? Clasificar los destinos de exportación de mayor a menor valor.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G16] Ranking de destinos")

ranking_destinos = (
    exp.groupby("PAIS_DEST_DESC")["FOB DOLAR"]
    .sum()
    .sort_values(ascending=True)
)
medallas = {0: "🥇", 1: "🥈", 2: "🥉"}   # top 3 desde el final (mayor primero)
etiq_ranking = list(ranking_destinos.index)

fig, ax = plt.subplots(figsize=(10, 5))
fig.suptitle("Ranking de Países Destino por FOB Exportado (Feb 2026)",
             fontsize=12, fontweight="bold")

colores_ranking = [PALETA[i % len(PALETA)] for i in range(len(ranking_destinos))]
barras = ax.barh(etiq_ranking, ranking_destinos.values,
                 color=colores_ranking, edgecolor="white", height=0.65)

for idx, (b, val) in enumerate(zip(reversed(barras), reversed(ranking_destinos.values))):
    posicion_desc = len(barras) - 1 - idx
    ax.text(val + val * 0.02, b.get_y() + b.get_height() / 2,
            f"${val:,.0f}", va="center", fontsize=8)

ax.set_xlabel("FOB (USD)")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e3:.0f}K"))
ax.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G16_ranking_destinos.png")


# ===========================================================================
# GRÁFICO 17 – CORRELACIÓN ENTRE VARIABLES NUMÉRICAS
# ¿Qué enseña? Descubrir qué variables se mueven juntas.
# Ejemplo: si FOB y KILO NETO tienen alta correlación, el precio es estable por kg.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G17] Correlación entre variables numéricas")

cols_correlacion = ["FOB DOLAR", "KILO NETO", "FLETE DOLAR",
                    "IMPONIBLE DOLAR", "DIAS_DESPACHO", "PRECIO_USD_KG"]
matriz_correlacion = datos[cols_correlacion].dropna().corr()

nombres_legibles = {
    "FOB DOLAR":       "FOB (USD)",
    "KILO NETO":       "Peso Neto",
    "FLETE DOLAR":     "Flete (USD)",
    "IMPONIBLE DOLAR": "Imponible",
    "DIAS_DESPACHO":   "Días Despacho",
    "PRECIO_USD_KG":   "USD/kg",
}
matriz_correlacion = matriz_correlacion.rename(index=nombres_legibles, columns=nombres_legibles)

fig, ax = plt.subplots(figsize=(8, 7))
fig.suptitle("Mapa de Correlación entre Variables Clave (Feb 2026)",
             fontsize=12, fontweight="bold")

mascara = np.triu(np.ones_like(matriz_correlacion, dtype=bool), k=1)
sns.heatmap(
    matriz_correlacion,
    ax=ax,
    annot=True,
    fmt=".2f",
    cmap="RdYlGn",
    center=0,
    vmin=-1, vmax=1,
    linewidths=0.5,
    cbar_kws={"label": "Coeficiente de Pearson"},
)
ax.set_title("(1.0 = correlación perfecta  |  -1.0 = correlación inversa)", fontsize=8)

plt.tight_layout()
guardar("G17_correlacion_variables.png")


# ===========================================================================
# GRÁFICO 18 – PONDERACIÓN DE TIPOS DE TRANSPORTE
# ¿Qué enseña? Comparar los medios de transporte en cuatro dimensiones.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G18] Ponderación de tipos de transporte")

transporte_metricas = (
    datos.groupby("MEDIO TRANSPORTE")
    .agg(
        cantidad_items   =("FOB DOLAR", "count"),
        fob_total        =("FOB DOLAR", "sum"),
        kilo_total       =("KILO NETO", "sum"),
        fob_promedio     =("FOB DOLAR", "mean"),
    )
    .reset_index()
)

medios = transporte_metricas["MEDIO TRANSPORTE"].tolist()
x      = np.arange(len(medios))
ancho  = 0.2

fig, ax = plt.subplots(figsize=(11, 5))
fig.suptitle("Comparativa de Medios de Transporte – Cuatro Métricas (Feb 2026)",
             fontsize=12, fontweight="bold")

metricas_transporte = [
    ("cantidad_items",   "Ítems",          1,   PALETA[0]),
    ("fob_total",        "FOB Total",       1e3, PALETA[1]),
    ("kilo_total",       "Kilos (miles)",   1e3, PALETA[2]),
    ("fob_promedio",     "FOB Promedio",    1e3, PALETA[3]),
]
for idx, (col, etiqueta, divisor, color) in enumerate(metricas_transporte):
    valores = transporte_metricas[col] / divisor
    barras  = ax.bar(x + idx * ancho, valores, ancho, label=etiqueta,
                     color=color, edgecolor="white", alpha=0.9)
    for b in barras:
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.02,
                f"{b.get_height():.1f}", ha="center", fontsize=7)

ax.set_xticks(x + ancho * 1.5)
ax.set_xticklabels(medios)
ax.legend(fontsize=8)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.set_ylabel("Valor (escala normalizada)")

plt.tight_layout()
guardar("G18_ponderacion_transporte.png")


# ===========================================================================
# GRÁFICO 19 – TOP 5 PRODUCTOS CON MAYOR CRECIMIENTO INTERANUAL
# ¿Qué enseña? Cuáles productos crecieron más entre el año anterior y el actual.
# Datos: SIMULADOS (comparativa anual 2024 vs 2025).
# ===========================================================================
print("[G19] Top 5 productos con mayor crecimiento")

productos_crec = ["Chia", "Textiles técnicos", "Moringa", "Canola", "Soja orgánica"]
fob_2024       = [22,  45, 12, 65, 110]   # millones USD
fob_2025       = [40,  78, 22, 92, 145]   # millones USD
tasas_crec     = [(b - a) / a * 100 for a, b in zip(fob_2024, fob_2025)]

posiciones = np.arange(len(productos_crec))
ancho      = 0.35

fig, (ax_barras, ax_tasa) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Top 5 Productos con Mayor Crecimiento Interanual (2024→2025)\n[Datos simulados]",
             fontsize=12, fontweight="bold")

# Panel izquierdo: barras agrupadas por año
b24 = ax_barras.bar(posiciones - ancho / 2, fob_2024, ancho,
                    label="2024", color=PALETA[6], edgecolor="white", alpha=0.85)
b25 = ax_barras.bar(posiciones + ancho / 2, fob_2025, ancho,
                    label="2025", color=VERDE, edgecolor="white", alpha=0.85)
ax_barras.set_xticks(posiciones)
ax_barras.set_xticklabels(productos_crec, rotation=20, ha="right")
ax_barras.set_ylabel("FOB (USD millones)")
ax_barras.legend()
ax_barras.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax_barras)

# Panel derecho: tasa de crecimiento
colores_tasa = [VERDE if t > 0 else ROJO for t in tasas_crec]
barras_tasa  = ax_tasa.bar(productos_crec, tasas_crec, color=colores_tasa, edgecolor="white", width=0.5)
for b, t in zip(barras_tasa, tasas_crec):
    ax_tasa.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
                 f"+{t:.0f}%", ha="center", fontsize=9, color=VERDE)
ax_tasa.axhline(0, color="#555", linewidth=0.9)
ax_tasa.set_ylabel("Variación (%)")
ax_tasa.set_title("Tasa de crecimiento 2024→2025")
ax_tasa.tick_params(axis="x", rotation=20, labelsize=8)
ax_tasa.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax_tasa)

plt.tight_layout()
guardar("G19_top5_productos_crecimiento.png")


# ===========================================================================
# GRÁFICO 20 – ÍNDICE DE CONCENTRACIÓN HERFINDAHL (HHI)
# ¿Qué enseña? Medir si el comercio está concentrado en pocos actores.
# Fórmula: HHI = Σ (si²)  donde si = participación en % de cada actor
# HHI < 1500 → mercado competitivo | 1500–2500 → moderado | > 2500 → concentrado
# Datos: REALES (febrero 2026) – calculado por país y por rubro.
# ===========================================================================
print("[G20] Índice Herfindahl (HHI)")

def calcular_hhi(serie_fob: pd.Series) -> float:
    """Calcula el Índice Herfindahl-Hirschman a partir de valores FOB."""
    participaciones = serie_fob / serie_fob.sum() * 100
    return (participaciones ** 2).sum()

hhi_paises = calcular_hhi(datos.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum())
hhi_rubros  = calcular_hhi(datos.groupby("RUBRO")["FOB DOLAR"].sum())
hhi_aduanas = calcular_hhi(datos.groupby("ADUANA")["FOB DOLAR"].sum())
hhi_transporte = calcular_hhi(datos.groupby("MEDIO TRANSPORTE")["FOB DOLAR"].sum())

categorias_hhi = ["Por País",    "Por Rubro",  "Por Aduana",  "Por Transporte"]
valores_hhi    = [hhi_paises,    hhi_rubros,    hhi_aduanas,   hhi_transporte]

def color_hhi(valor):
    if valor < 1500:  return VERDE
    elif valor < 2500: return NARANJA
    else:              return ROJO

fig, ax = plt.subplots(figsize=(9, 5))
fig.suptitle("Índice de Concentración Herfindahl-Hirschman (HHI) (Feb 2026)",
             fontsize=12, fontweight="bold")

barras = ax.bar(categorias_hhi, valores_hhi,
                color=[color_hhi(v) for v in valores_hhi], edgecolor="white", width=0.55)
for b, v in zip(barras, valores_hhi):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 50,
            f"HHI = {v:.0f}", ha="center", fontsize=9, fontweight="bold")

ax.axhline(1500, color=NARANJA, linestyle="--", linewidth=1.2, alpha=0.7)
ax.axhline(2500, color=ROJO,    linestyle="--", linewidth=1.2, alpha=0.7)
ax.text(3.6, 1520, "1.500 → moderado", fontsize=7.5, color=NARANJA)
ax.text(3.6, 2520, "2.500 → concentrado", fontsize=7.5, color=ROJO)

leyenda = [
    mpatches.Patch(color=VERDE,   label="Competitivo (< 1500)"),
    mpatches.Patch(color=NARANJA, label="Moderado (1500–2500)"),
    mpatches.Patch(color=ROJO,    label="Concentrado (> 2500)"),
]
ax.legend(handles=leyenda, fontsize=8)
ax.set_ylabel("HHI")
ax.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G20_herfindahl_hhi.png")


# ===========================================================================
# GRÁFICO 21 – COMPORTAMIENTO POR TRIMESTRE
# ¿Qué enseña? Ver la estacionalidad trimestral y comparar años.
# Q1 (ene-mar) suele ser el más alto en Paraguay por la cosecha de soja.
# Datos: SIMULADOS.
# ===========================================================================
print("[G21] Comportamiento por trimestre")

trimestres      = ["Q1", "Q2", "Q3", "Q4"]
exportaciones_q = {
    2023: [2200, 1800, 1600, 1700],
    2024: [2450, 2000, 1750, 1900],
    2025: [2700, 2150, 1900, 2050],
}

fig, ax = plt.subplots(figsize=(10, 5))
fig.suptitle("Exportaciones por Trimestre (USD millones)\n[Datos simulados]",
             fontsize=12, fontweight="bold")

marcadores = ["o", "s", "^"]
for (anio, valores), marcador in zip(exportaciones_q.items(), marcadores):
    ax.plot(trimestres, valores, marker=marcador, label=str(anio),
            linewidth=2.5, markersize=8)
    for x, y in zip(trimestres, valores):
        ax.text(x, y + 25, f"${y}M", ha="center", fontsize=7.5)

ax.set_ylabel("USD Millones")
ax.set_title("Q1 = Ene-Mar (temporada alta de cosecha)")
ax.legend(title="Año")
ax.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax)

plt.tight_layout()
guardar("G21_comportamiento_trimestral.png")


# ===========================================================================
# GRÁFICO 22 – BRECHAS ENTRE PLANIFICACIÓN Y EJECUCIÓN
# ¿Qué enseña? Comparar las metas de exportación con los resultados reales.
# Una brecha negativa indica sub-ejecución; positiva, superávit de rendimiento.
# Datos: SIMULADOS.
# ===========================================================================
print("[G22] Brechas planificación vs ejecución")

meses_sem2 = ["Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
meta_mensual   = [95, 98, 102, 110, 108, 100]   # USD millones
real_mensual   = [88, 102, 99, 115, 103, 97]
brecha         = [r - m for r, m in zip(real_mensual, meta_mensual)]

fig, (ax_comp, ax_brecha) = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
fig.suptitle("Planificación vs Ejecución de Exportaciones (2S 2025)\n[Datos simulados]",
             fontsize=12, fontweight="bold")

# Panel superior: meta vs real
ax_comp.plot(meses_sem2, meta_mensual, marker="s", color=NARANJA, linewidth=2,
             linestyle="--", label="Meta", markersize=7)
ax_comp.plot(meses_sem2, real_mensual, marker="o", color=VERDE, linewidth=2.5,
             label="Real", markersize=7)
ax_comp.fill_between(meses_sem2, meta_mensual, real_mensual, alpha=0.12,
                     where=[r > m for r, m in zip(real_mensual, meta_mensual)], color=VERDE)
ax_comp.fill_between(meses_sem2, meta_mensual, real_mensual, alpha=0.12,
                     where=[r < m for r, m in zip(real_mensual, meta_mensual)], color=ROJO)
ax_comp.set_ylabel("USD Millones")
ax_comp.legend()
ax_comp.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax_comp)

# Panel inferior: brecha
colores_brecha = [VERDE if b >= 0 else ROJO for b in brecha]
barras_br      = ax_brecha.bar(meses_sem2, brecha, color=colores_brecha, edgecolor="white", width=0.55)
for b, val in zip(barras_br, brecha):
    ax_brecha.text(b.get_x() + b.get_width() / 2,
                   b.get_height() + (0.3 if val >= 0 else -1),
                   f"{val:+.0f}", ha="center", fontsize=9)
ax_brecha.axhline(0, color="#555", linewidth=1)
ax_brecha.set_ylabel("Brecha (USD millones)")
ax_brecha.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G22_brechas_planificacion.png")


# ===========================================================================
# GRÁFICO 23 – PRODUCTOS CON MAYOR FRECUENCIA DE DESPACHO
# ¿Qué enseña? Cuáles rubros tienen más operaciones (no necesariamente más valor).
# Alta frecuencia → producto de ciclo corto o demanda constante.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G23] Productos con mayor frecuencia de despacho")

frecuencia_rubro = (
    datos.groupby("RUBRO")
    .agg(cantidad_despachos=("DESPACHO CIFRADO", "nunique"),
         fob_promedio=("FOB DOLAR", "mean"))
    .sort_values("cantidad_despachos", ascending=True)
    .tail(10)
)
etiq_frec = [r[:35] + "…" if len(r) > 35 else r for r in frecuencia_rubro.index]

fig, ax = plt.subplots(figsize=(11, 6))
fig.suptitle("Frecuencia de Despachos por Rubro (Feb 2026)", fontsize=12, fontweight="bold")

barras = ax.barh(etiq_frec, frecuencia_rubro["cantidad_despachos"],
                 color=PALETA[:len(frecuencia_rubro)], edgecolor="white", height=0.65)
for b, (_, fila) in zip(barras, frecuencia_rubro.iterrows()):
    ax.text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2,
            f"{b.get_width():.0f} desp. | prom ${fila['fob_promedio']:,.0f}",
            va="center", fontsize=7.5)

ax.set_xlabel("Cantidad de despachos únicos")
ax.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G23_frecuencia_despachos.png")


# ===========================================================================
# GRÁFICO 24 – MAPA DE CALOR POR REGIÓN (PAÍS × TRANSPORTE)
# ¿Qué enseña? Qué medio de transporte se usa para cada destino.
# Útil para entender la logística según la geografía del destino.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G24] Mapa de calor país × transporte")

tabla_calor = (
    datos.groupby(["PAIS_DEST_DESC", "MEDIO TRANSPORTE"])["FOB DOLAR"]
    .sum()
    .unstack(fill_value=0)
)
etiq_calor = [p[:15] + "…" if len(p) > 15 else p for p in tabla_calor.index]

fig, ax = plt.subplots(figsize=(9, 7))
fig.suptitle("FOB USD por País y Medio de Transporte (Feb 2026)",
             fontsize=12, fontweight="bold")

sns.heatmap(
    tabla_calor,
    ax=ax,
    annot=True,
    fmt=".0f",
    cmap="Blues",
    linewidths=0.5,
    yticklabels=etiq_calor,
    cbar_kws={"label": "FOB (USD)"},
)
ax.set_xlabel("Medio de transporte")
ax.set_ylabel("País destino")

plt.tight_layout()
guardar("G24_heatmap_pais_transporte.png")


# ===========================================================================
# GRÁFICO 25 – ANÁLISIS DE RIESGO PAÍS
# ¿Qué enseña? Cruzar el volumen exportado hacia un país con su nivel de riesgo.
# Países de alto riesgo requieren mayores garantías o coberturas de seguro.
# Datos: SIMULADOS (puntaje de riesgo basado en índices internacionales).
# ===========================================================================
print("[G25] Análisis de riesgo país")

riesgo_paises = {
    "BRASIL":                      {"riesgo": 35, "fob": exp.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum().get("BRASIL", 50000)},
    "REINO UNIDO":                 {"riesgo": 15, "fob": exp.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum().get("REINO UNIDO", 100000)},
    "VIETNAM":                     {"riesgo": 45, "fob": exp.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum().get("VIETNAM", 33000)},
    "BOLIVIA":                     {"riesgo": 55, "fob": exp.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum().get("BOLIVIA", 25000)},
    "URUGUAY":                     {"riesgo": 28, "fob": exp.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum().get("URUGUAY", 15000)},
    "INDIA":                       {"riesgo": 42, "fob": 15000},
    "ALEMANIA":                    {"riesgo": 10, "fob": 12000},
    "ESTADOS UNIDOS DE AMERICA":   {"riesgo": 12, "fob": 8000},
    "ESPAÑA":                      {"riesgo": 18, "fob": 6000},
}

fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle("Matriz de Riesgo País vs Volumen Exportado\n[Puntaje de riesgo simulado]",
             fontsize=12, fontweight="bold")

for pais, info in riesgo_paises.items():
    color = ROJO if info["riesgo"] > 40 else (NARANJA if info["riesgo"] > 25 else VERDE)
    ax.scatter(info["riesgo"], info["fob"] / 1e3, s=info["fob"] / 500,
               color=color, alpha=0.75, edgecolors="white", linewidths=1.2)
    ax.text(info["riesgo"] + 0.5, info["fob"] / 1e3 + 0.5, pais[:12],
            fontsize=7.5, color="#333")

ax.axvline(25, color=NARANJA, linestyle="--", linewidth=1, alpha=0.6)
ax.axvline(40, color=ROJO,    linestyle="--", linewidth=1, alpha=0.6)
ax.set_xlabel("Puntaje de riesgo país (0 = bajo, 100 = alto)")
ax.set_ylabel("FOB exportado (USD miles)")
ax.grid(linestyle="--", alpha=0.35)
nota_simulado(ax, "Puntaje de riesgo simulado con fines pedagógicos")

leyenda_riesgo = [
    mpatches.Patch(color=VERDE,   label="Bajo riesgo (< 25)"),
    mpatches.Patch(color=NARANJA, label="Riesgo medio (25–40)"),
    mpatches.Patch(color=ROJO,    label="Alto riesgo (> 40)"),
]
ax.legend(handles=leyenda_riesgo, fontsize=8, loc="upper right")

plt.tight_layout()
guardar("G25_riesgo_pais.png")


# ===========================================================================
# GRÁFICO 26 – EVOLUCIÓN DE COSTOS LOGÍSTICOS (RATIO FLETE/FOB)
# ¿Qué enseña? Qué porcentaje del valor de la mercancía se va en flete.
# Un ratio alto puede erosionar la competitividad del exportador.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G26] Evolución de costos logísticos")

flete_por_transporte = (
    datos.groupby("MEDIO TRANSPORTE")
    .agg(fob=("FOB DOLAR", "sum"), flete=("FLETE DOLAR", "sum"))
    .assign(ratio_pct=lambda df: df["flete"] / df["fob"] * 100)
    .reset_index()
)
flete_por_rubro = (
    datos[datos["FLETE DOLAR"] > 0]
    .groupby("RUBRO")
    .agg(fob=("FOB DOLAR", "sum"), flete=("FLETE DOLAR", "sum"))
    .assign(ratio_pct=lambda df: df["flete"] / df["fob"] * 100)
    .sort_values("ratio_pct", ascending=True)
    .tail(8)
)

fig, (ax_trans, ax_rubro) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Ratio Flete / FOB: Costo Logístico Relativo (Feb 2026)",
             fontsize=12, fontweight="bold")

# Panel izquierdo: por medio de transporte
ax_trans.bar(flete_por_transporte["MEDIO TRANSPORTE"],
             flete_por_transporte["ratio_pct"],
             color=PALETA[:3], edgecolor="white", width=0.5)
for i, fila in flete_por_transporte.iterrows():
    ax_trans.text(i, fila["ratio_pct"] + 0.3, f"{fila['ratio_pct']:.1f}%",
                  ha="center", fontsize=9)
ax_trans.set_ylabel("Flete como % del FOB")
ax_trans.set_title("Por medio de transporte")
ax_trans.grid(axis="y", linestyle="--", alpha=0.4)

# Panel derecho: por rubro
etiq_rubro = [r[:30] + "…" if len(r) > 30 else r for r in flete_por_rubro.index]
ax_rubro.barh(etiq_rubro, flete_por_rubro["ratio_pct"],
              color=PALETA[:len(flete_por_rubro)], edgecolor="white", height=0.65)
ax_rubro.set_xlabel("Flete como % del FOB")
ax_rubro.set_title("Por rubro de mercancía")
ax_rubro.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G26_costos_logisticos.png")


# ===========================================================================
# GRÁFICO 27 – IDENTIFICACIÓN DE OUTLIERS EN FOB
# ¿Qué enseña? Detectar despachos con valores inusualmente altos o bajos.
# Los outliers pueden indicar errores de carga, mercancías especiales o fraude.
# Datos: REALES (febrero 2026).
# ===========================================================================
print("[G27] Identificación de outliers")

fig, (ax_box, ax_scatter) = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("Detección de Valores Atípicos (Outliers) en FOB USD (Feb 2026)",
             fontsize=12, fontweight="bold")

# Panel izquierdo: diagrama de caja
bp = ax_box.boxplot(
    [exp["FOB DOLAR"].dropna(), imp["FOB DOLAR"].dropna()],
    tick_labels=["Exportación", "Importación"],
    patch_artist=True,
    medianprops={"color": "white", "linewidth": 2},
    flierprops={"marker": "o", "markersize": 6, "alpha": 0.7,
                "markeredgecolor": ROJO, "markerfacecolor": ROJO},
)
for parche, color in zip(bp["boxes"], [VERDE, ROJO]):
    parche.set_facecolor(color)
    parche.set_alpha(0.7)
ax_box.set_ylabel("FOB (USD)")
ax_box.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e3:.0f}K"))
ax_box.set_title("Distribución por operación")
ax_box.grid(axis="y", linestyle="--", alpha=0.4)

# Panel derecho: cada despacho como punto
for operacion, color in [("EXPORTACION", VERDE), ("IMPORTACION", ROJO)]:
    subset = datos[datos["OPERACION"] == operacion].reset_index(drop=True)
    ax_scatter.scatter(range(len(subset)), subset["FOB DOLAR"],
                       color=color, alpha=0.7, s=50, edgecolors="white",
                       linewidths=0.7, label=operacion)

# Línea de outlier superior (percentil 95)
p95 = datos["FOB DOLAR"].quantile(0.95)
ax_scatter.axhline(p95, color=NARANJA, linestyle="--", linewidth=1.5, alpha=0.8)
ax_scatter.text(0, p95 + 5000, f"P95 = ${p95:,.0f}", fontsize=7.5, color=NARANJA)
ax_scatter.set_xlabel("Índice del despacho")
ax_scatter.set_ylabel("FOB (USD)")
ax_scatter.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v/1e3:.0f}K"))
ax_scatter.set_title("Todos los despachos individuales")
ax_scatter.legend()
ax_scatter.grid(linestyle="--", alpha=0.35)

plt.tight_layout()
guardar("G27_outliers_fob.png")


# ===========================================================================
# GRÁFICO 28 – ANÁLISIS DE SOSTENIBILIDAD: HUELLA DE CARBONO POR RUBRO
# ¿Qué enseña? Estimar las emisiones de CO2 según el medio de transporte usado.
# Factores de emisión estándar (kg CO2 por tonelada-km):
#   Aéreo: 0.602  |  Marítimo: 0.016  |  Terrestre: 0.096
# Datos: REALES (peso y transporte) + factores de emisión estándar (simulados).
# ===========================================================================
print("[G28] Análisis de sostenibilidad (huella de carbono)")

FACTOR_EMISION_CO2 = {"AVION": 0.602, "ACUATICO": 0.016, "CAMION": 0.096}
DISTANCIA_PROMEDIO = {"AVION": 8000,  "ACUATICO": 4000,  "CAMION": 600}

datos_carbon = datos.copy()
datos_carbon["TONELADAS"]   = datos_carbon["KILO NETO"] / 1000
datos_carbon["DISTANCIA"]   = datos_carbon["MEDIO TRANSPORTE"].map(DISTANCIA_PROMEDIO).fillna(1000)
datos_carbon["FACTOR_CO2"]  = datos_carbon["MEDIO TRANSPORTE"].map(FACTOR_EMISION_CO2).fillna(0.1)
datos_carbon["CO2_KG"]      = datos_carbon["TONELADAS"] * datos_carbon["DISTANCIA"] * datos_carbon["FACTOR_CO2"]

carbon_por_transporte = datos_carbon.groupby("MEDIO TRANSPORTE")["CO2_KG"].sum()
carbon_por_rubro      = (
    datos_carbon.groupby("RUBRO")["CO2_KG"]
    .sum()
    .sort_values(ascending=True)
    .tail(8)
)
etiq_carbon = [r[:30] + "…" if len(r) > 30 else r for r in carbon_por_rubro.index]

fig, (ax_trans, ax_rubro) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Huella de Carbono Estimada por Transporte y Rubro (Feb 2026)\n"
             "[Factores de emisión estándar ICAO/IMO]",
             fontsize=12, fontweight="bold")

colores_carbon = {"ACUATICO": "#259B9A", "AVION": "#D4285B", "CAMION": "#E8A838"}
ax_trans.bar(carbon_por_transporte.index,
             carbon_por_transporte.values / 1000,   # convertir a toneladas CO2
             color=[colores_carbon.get(t, AZUL) for t in carbon_por_transporte.index],
             edgecolor="white", width=0.5)
for i, (transp, val) in enumerate(carbon_por_transporte.items()):
    ax_trans.text(i, val / 1000 + 0.05, f"{val/1000:.2f} t CO₂",
                  ha="center", fontsize=9)
ax_trans.set_ylabel("CO₂ estimado (toneladas)")
ax_trans.set_title("Por medio de transporte")
ax_trans.grid(axis="y", linestyle="--", alpha=0.4)

ax_rubro.barh(etiq_carbon, carbon_por_rubro.values / 1000,
              color=PALETA[:len(carbon_por_rubro)], edgecolor="white", height=0.65)
ax_rubro.set_xlabel("CO₂ estimado (toneladas)")
ax_rubro.set_title("Por rubro de mercancía")
ax_rubro.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
guardar("G28_huella_carbono.png")


# ===========================================================================
# GRÁFICO 29 – EFECTO DE LA PANDEMIA EN EXPORTACIONES CLAVE
# ¿Qué enseña? Visualizar el impacto del COVID-19 en los principales rubros.
# La pandemia afectó logística, demanda y precios globales en 2020-2021.
# Datos: SIMULADOS (serie histórica 2018–2026).
# ===========================================================================
print("[G29] Efecto de la pandemia en exportaciones clave")

anios_pandemia   = list(range(2018, 2027))
rubros_pandemia  = {
    "Oleaginosas":  [780, 820, 600, 750, 920, 880, 950, 1010, 1080],
    "Carne bovina": [310, 340, 220, 290, 380, 420, 450, 490,  520],
    "Textiles":     [180, 195, 120, 160, 210, 240, 260, 285,  310],
}

fig, ax = plt.subplots(figsize=(13, 6))
fig.suptitle("Efecto de la Pandemia COVID-19 en Exportaciones Clave (2018–2026)\n[Datos simulados]",
             fontsize=12, fontweight="bold")

for (rubro, valores), color in zip(rubros_pandemia.items(), PALETA[:3]):
    ax.plot(anios_pandemia, valores, marker="o", label=rubro, color=color,
            linewidth=2.5, markersize=7)
    for x, y in zip(anios_pandemia, valores):
        ax.text(x, y + 8, str(y), ha="center", fontsize=6.5, color="#555")

ax.axvspan(2019.6, 2021.4, alpha=0.07, color="red")
ax.text(2020.5, ax.get_ylim()[1] * 0.97, "Pandemia\nCOVID-19",
        ha="center", va="top", fontsize=9, color="red",
        bbox=dict(boxstyle="round", facecolor="white", edgecolor="red", alpha=0.8))

ax.axvspan(2021.4, 2022.6, alpha=0.05, color=VERDE)
ax.text(2022, ax.get_ylim()[1] * 0.88, "Recuperación",
        ha="center", fontsize=8, color=VERDE)

ax.set_xlabel("Año")
ax.set_ylabel("FOB (USD millones)")
ax.legend()
ax.grid(axis="y", linestyle="--", alpha=0.4)
nota_simulado(ax)

plt.tight_layout()
guardar("G29_efecto_pandemia.png")


# ===========================================================================
# GRÁFICO 30 – VISUALIZACIÓN GEOESPACIAL DE VOLUMEN
# ¿Qué enseña? Mostrar los países de destino en un plano de coordenadas
# (latitud/longitud) con burbujas proporcionales al FOB exportado.
# Útil para visualizar qué tan diversificada está la oferta exportadora.
# Datos: REALES (valores FOB) + coordenadas geográficas (referencia manual).
# ===========================================================================
print("[G30] Visualización geoespacial de volumen")

COORDENADAS_PAISES = {
    "BRASIL":                     (-52, -14),
    "INDIA":                      ( 79,  22),
    "REINO UNIDO":                ( -2,  54),
    "ALEMANIA":                   ( 10,  51),
    "VIETNAM":                    (108,  16),
    "URUGUAY":                    (-56, -33),
    "ESTADOS UNIDOS DE AMERICA":  (-100, 38),
    "BOLIVIA":                    (-65, -17),
    "ESPAÑA":                     ( -4,  40),
}
PARAGUAY_COORD = (-58, -23)

fob_por_pais_geo = datos.groupby("PAIS_DEST_DESC")["FOB DOLAR"].sum()

fig, ax = plt.subplots(figsize=(14, 8))
fig.suptitle("Distribución Geoespacial de Flujos Comerciales – Paraguay (Feb 2026)\n"
             "Tamaño de burbuja = FOB USD total",
             fontsize=12, fontweight="bold")

ax.set_facecolor("#E8F4FD")
ax.set_xlim(-160, 160)
ax.set_ylim(-60, 70)
ax.axhline(0, color="#C0D8E8", linewidth=0.8, linestyle="--")
ax.axvline(0, color="#C0D8E8", linewidth=0.8, linestyle="--")
ax.set_xlabel("Longitud")
ax.set_ylabel("Latitud")
ax.set_xticks(range(-150, 160, 30))
ax.set_yticks(range(-60, 70, 20))
ax.grid(color="#C0D8E8", linewidth=0.5, alpha=0.6)

# Punto de origen: Paraguay
ax.scatter(*PARAGUAY_COORD, s=250, color="#FFD700", zorder=10,
           marker="*", edgecolors="#555", linewidths=0.8)
ax.text(PARAGUAY_COORD[0] + 1, PARAGUAY_COORD[1] - 3,
        "PARAGUAY\n(Origen)", fontsize=8, color="#555", ha="left")

# Burbujas por país destino
escala_burbuja = 80 / fob_por_pais_geo.max()   # normalizar tamaño

for pais, fob in fob_por_pais_geo.items():
    if pais not in COORDENADAS_PAISES:
        continue
    lon, lat    = COORDENADAS_PAISES[pais]
    tamaño      = max(fob * escala_burbuja * 1000, 300)
    operacion   = datos[datos["PAIS_DEST_DESC"] == pais]["OPERACION"].mode()[0]
    color_pais  = VERDE if operacion == "EXPORTACION" else ROJO

    ax.scatter(lon, lat, s=tamaño, color=color_pais, alpha=0.65,
               edgecolors="white", linewidths=1.2, zorder=5)
    ax.annotate(
        f"{pais[:10]}\n${fob/1e3:.0f}K",
        xy=(lon, lat),
        xytext=(lon + 5, lat + 4),
        fontsize=7,
        color="#333",
        arrowprops={"arrowstyle": "->", "color": "#aaa", "lw": 0.8},
    )
    ax.plot([PARAGUAY_COORD[0], lon], [PARAGUAY_COORD[1], lat],
            color=color_pais, linewidth=0.8, alpha=0.4, linestyle="--")

leyenda_geo = [
    mpatches.Patch(color=VERDE,   label="País de exportación"),
    mpatches.Patch(color=ROJO,    label="País de importación"),
    plt.Line2D([0], [0], marker="*", color="w", markerfacecolor="#FFD700",
               markersize=12, label="Paraguay (origen)"),
]
ax.legend(handles=leyenda_geo, loc="lower left", fontsize=8)

plt.tight_layout()
guardar("G30_geoespacial.png")


# ─────────────────────────────────────────────────────────────────────────────
# SECCIÓN FINAL – RESUMEN DE GRÁFICOS GENERADOS
# ─────────────────────────────────────────────────────────────────────────────
graficos_generados = sorted(CARPETA_SALIDA.glob("*.png"))
print("\n" + "=" * 65)
print(f"  PROCESO COMPLETADO – {len(graficos_generados)} gráficos generados")
print(f"  Carpeta de salida: {CARPETA_SALIDA}")
print("=" * 65)
print("\n  Gráficos con datos REALES (Feb 2026):")
print("    G02 G03 G06 G07 G08 G10 G11 G12 G14 G15 G16 G17 G18 G20")
print("    G23 G24 G26 G27 G28 G30")
print("\n  Gráficos con datos SIMULADOS (con fines pedagógicos):")
print("    G01 G04 G05 G09 G13 G19 G21 G22 G25 G29")
print()
