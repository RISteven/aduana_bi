"""
=======================================================================
ANÁLISIS DE DATOS ADUANEROS – Febrero 2026
=======================================================================
Este script lee los datos limpios del data lake (capa Silver),
realiza 8 análisis y genera gráficos explicativos.

Librerías usadas:
  - duckdb    → leer archivos .parquet con SQL
  - pandas    → manipular y resumir los datos como tablas
  - matplotlib → crear los gráficos
  - pathlib   → manejar rutas de carpetas de forma portátil
=======================================================================
"""

# ── 1. IMPORTAR LIBRERÍAS ──────────────────────────────────────────────────
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from pathlib import Path


# ── 2. DEFINIR RUTAS ──────────────────────────────────────────────────────
# Path(__file__) devuelve la ruta de ESTE archivo.
# .parent sube un nivel de carpeta.
carpeta_proyecto   = Path(__file__).parent.parent
archivo_datos      = carpeta_proyecto / "data_lake" / "silver" / "aduana_item_clean.parquet"
carpeta_graficos   = Path(__file__).parent / "graficos"

# Crear la carpeta de gráficos si todavía no existe
carpeta_graficos.mkdir(parents=True, exist_ok=True)



COLOR_EXPORTACION  = "#016948"   # Dark Blue (primario Columbia)
COLOR_IMPORTACION  = "#B44365"   # Magenta   (terciario Columbia)
PALETA_COLORES     = [
    "#012169",   # Dark Blue
    "#D4285B",   # Magenta
    "#009EFF",   # Medium Blue
    "#259B9A",   # Turquoise
    "#6CACE4",   # Light Blue
    "#7B2A8D",   # Purple
    "#4A4A4A",   # Gris oscuro (neutro)
    "#AAAAAA",   # Gris claro  (neutro)
]

# Opciones estéticas generales para matplotlib
plt.rcParams.update({
    "font.family":        "DejaVu Sans",
    "axes.spines.top":    False,   # ocultar borde superior
    "axes.spines.right":  False,   # ocultar borde derecho
    "figure.dpi":         120,
})


# ── 4. CARGAR LOS DATOS ───────────────────────────────────────────────────
# Abrimos una conexión en memoria con DuckDB y leemos el parquet como SQL
conexion = duckdb.connect()
consulta_sql = f"SELECT * FROM '{archivo_datos}'"
datos = conexion.execute(consulta_sql).fetchdf()   # fetchdf() → DataFrame de pandas

# Algunas columnas de tributos llegaron como texto; las convertimos a número
columnas_tributarias = ["DERECHO", "IVA", "ISC", "RENTA", "OTROS", "TOTAL",
                        "SERVICIO", "COTIZACION"]
for nombre_columna in columnas_tributarias:
    datos[nombre_columna] = pd.to_numeric(datos[nombre_columna], errors="coerce")
    # errors="coerce" reemplaza valores que no se pueden convertir con NaN

# Confirmamos cuántos registros cargamos
cantidad_registros  = len(datos)
resumen_operaciones = datos["OPERACION"].value_counts().to_dict()
print(f"✔ Datos cargados: {cantidad_registros} registros")
print(f"  Distribución: {resumen_operaciones}")


# =======================================================================
# GRÁFICO 1 – Exportaciones vs Importaciones (cantidad y FOB)
# =======================================================================
figura, ejes = plt.subplots(1, 2, figsize=(10, 5))
figura.suptitle(
    "Distribución: Exportaciones vs Importaciones\nFebrero 2026",
    fontsize=13, fontweight="bold"
)

# Calculamos los totales que queremos mostrar
cantidad_por_operacion = datos["OPERACION"].value_counts()
fob_por_operacion      = datos.groupby("OPERACION")["FOB DOLAR"].sum()

# Iteramos sobre los dos subgráficos (tortas)
pares = [
    (ejes[0], cantidad_por_operacion, "Cantidad de ítems"),
    (ejes[1], fob_por_operacion,      "FOB total (USD)"),
]
for eje, serie, titulo_sub in pares:
    colores_sector = [
        COLOR_EXPORTACION if "EXP" in etiqueta else COLOR_IMPORTACION
        for etiqueta in serie.index
    ]
    sectores, textos, porcentajes = eje.pie(
        serie,
        labels=serie.index,
        autopct="%1.1f%%",
        colors=colores_sector,
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": 9},
    )
    # Mejorar legibilidad de los porcentajes dentro del gráfico
    for texto_pct in porcentajes:
        texto_pct.set_fontsize(9)
        texto_pct.set_color("white")
        texto_pct.set_fontweight("bold")
    eje.set_title(titulo_sub, fontsize=10, pad=10)

plt.tight_layout()
ruta_salida = carpeta_graficos / "01_importacion_vs_exportacion.png"
plt.savefig(ruta_salida, bbox_inches="tight")
plt.show()
print(f"✔ Gráfico 1 guardado: {ruta_salida.name}")


# =======================================================================
# GRÁFICO 2 – Top 8 países de destino/origen por FOB USD
# =======================================================================
figura, eje = plt.subplots(figsize=(10, 5))
figura.suptitle(
    "FOB USD por País de Destino/Origen (Top 8)\nFebrero 2026",
    fontsize=13, fontweight="bold"
)

# Agrupamos: para cada país y tipo de operación, sumamos el FOB
fob_por_pais = (
    datos
    .groupby(["PAIS_DEST_DESC", "OPERACION"])["FOB DOLAR"]
    .sum()
    .unstack(fill_value=0)       # cada operación pasa a ser una columna
    .sort_values(                 # ordenamos de mayor a menor exportación
        by=[c for c in ["EXPORTACION", "IMPORTACION"] if c in datos["OPERACION"].unique()][0],
        ascending=False
    )
    .head(8)
)

posiciones_x  = range(len(fob_por_pais))
ancho_barra   = 0.38
operaciones   = [c for c in ["EXPORTACION", "IMPORTACION"] if c in fob_por_pais.columns]

for indice_op, nombre_op in enumerate(operaciones):
    color  = COLOR_EXPORTACION if nombre_op == "EXPORTACION" else COLOR_IMPORTACION
    offset = (indice_op - 0.5) * ancho_barra   # desplazamiento para barras agrupadas

    barras = eje.bar(
        [x + offset for x in posiciones_x],
        fob_por_pais[nombre_op],
        width=ancho_barra,
        label=nombre_op,
        color=color,
        alpha=0.88,
        edgecolor="white"
    )
    # Etiqueta encima de cada barra
    for barra in barras:
        altura = barra.get_height()
        if altura > 0:
            eje.text(
                barra.get_x() + barra.get_width() / 2,
                altura + 2000,
                f"${altura / 1e3:.0f}K",
                ha="center", va="bottom", fontsize=7.5, color="#333333"
            )

eje.set_xticks(list(posiciones_x))
eje.set_xticklabels(fob_por_pais.index, rotation=30, ha="right", fontsize=8.5)
eje.yaxis.set_major_formatter(mticker.FuncFormatter(lambda valor, _: f"${valor / 1e3:.0f}K"))
eje.set_ylabel("FOB (USD)", fontsize=9)
eje.legend(fontsize=9)
eje.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
ruta_salida = carpeta_graficos / "02_fob_por_pais.png"
plt.savefig(ruta_salida, bbox_inches="tight")
plt.show()
print(f"✔ Gráfico 2 guardado: {ruta_salida.name}")


# =======================================================================
# GRÁFICO 3 – Top rubros de mercadería por FOB USD
# =======================================================================
figura, eje = plt.subplots(figsize=(10, 5))
figura.suptitle(
    "Top Rubros por FOB USD\nFebrero 2026",
    fontsize=13, fontweight="bold"
)

fob_por_rubro = (
    datos
    .groupby("RUBRO")["FOB DOLAR"]
    .sum()
    .sort_values(ascending=True)   # ascending=True para que el mayor quede arriba en barh
    .tail(8)
)

# Acortamos las etiquetas largas para que entren en el gráfico
etiquetas_cortas = [
    nombre[:45] + "…" if len(nombre) > 45 else nombre
    for nombre in fob_por_rubro.index
]

barras = eje.barh(
    etiquetas_cortas,
    fob_por_rubro.values,
    color=PALETA_COLORES[:len(fob_por_rubro)],
    edgecolor="white",
    height=0.65
)
for barra in barras:
    ancho = barra.get_width()
    eje.text(
        ancho + 5000,
        barra.get_y() + barra.get_height() / 2,
        f"${ancho / 1e3:.0f}K",
        va="center", fontsize=8
    )

eje.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v / 1e3:.0f}K"))
eje.set_xlabel("FOB (USD)", fontsize=9)
eje.tick_params(axis="y", labelsize=8)
eje.grid(axis="x", linestyle="--", alpha=0.4)

plt.tight_layout()
ruta_salida = carpeta_graficos / "03_fob_por_rubro.png"
plt.savefig(ruta_salida, bbox_inches="tight")
plt.show()
print(f"✔ Gráfico 3 guardado: {ruta_salida.name}")


# =======================================================================
# GRÁFICO 4 – FOB por aduana (barras apiladas Exp / Imp)
# =======================================================================
figura, eje = plt.subplots(figsize=(10, 5))
figura.suptitle(
    "FOB USD por Aduana y Tipo de Operación\nFebrero 2026",
    fontsize=13, fontweight="bold"
)

# Tabla pivote: filas = aduanas, columnas = tipo de operación
fob_por_aduana = (
    datos
    .groupby(["ADUANA", "OPERACION"])["FOB DOLAR"]
    .sum()
    .unstack(fill_value=0)
    .sort_values(
        by=[c for c in ["EXPORTACION", "IMPORTACION"] if c in datos["OPERACION"].unique()][0],
        ascending=False
    )
)

posiciones_x = range(len(fob_por_aduana))
base_acumulada = pd.Series([0.0] * len(fob_por_aduana), index=fob_por_aduana.index)
operaciones    = [c for c in ["EXPORTACION", "IMPORTACION"] if c in fob_por_aduana.columns]
color_por_op   = {"EXPORTACION": COLOR_EXPORTACION, "IMPORTACION": COLOR_IMPORTACION}

for nombre_op in operaciones:
    valores = fob_por_aduana[nombre_op]
    eje.bar(
        posiciones_x,
        valores,
        bottom=base_acumulada.values,
        label=nombre_op,
        color=color_por_op[nombre_op],
        alpha=0.88,
        edgecolor="white"
    )
    base_acumulada = base_acumulada + valores   # apilamos sobre la base anterior

# Etiqueta total arriba de cada barra
total_por_aduana = fob_por_aduana.sum(axis=1)
for indice, (nombre_aduana, total) in enumerate(total_por_aduana.items()):
    eje.text(
        indice, total + 5000,
        f"${total / 1e3:.0f}K",
        ha="center", va="bottom", fontsize=8, color="#333"
    )

eje.set_xticks(list(posiciones_x))
eje.set_xticklabels(fob_por_aduana.index, rotation=30, ha="right", fontsize=8.5)
eje.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v / 1e3:.0f}K"))
eje.set_ylabel("FOB (USD)", fontsize=9)
eje.legend(fontsize=9)
eje.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()
ruta_salida = carpeta_graficos / "04_fob_por_aduana.png"
plt.savefig(ruta_salida, bbox_inches="tight")
plt.show()
print(f"✔ Gráfico 4 guardado: {ruta_salida.name}")


# =======================================================================
# GRÁFICO 5 – Medio de transporte: cantidad de ítems y FOB
# =======================================================================
figura, ejes = plt.subplots(1, 2, figsize=(10, 4))
figura.suptitle(
    "Medio de Transporte\nFebrero 2026",
    fontsize=13, fontweight="bold"
)

cantidad_por_transporte = datos["MEDIO TRANSPORTE"].value_counts()
fob_por_transporte      = datos.groupby("MEDIO TRANSPORTE")["FOB DOLAR"].sum()

pares = [
    (ejes[0], cantidad_por_transporte, "Cantidad de ítems"),
    (ejes[1], fob_por_transporte,      "FOB total (USD)"),
]
for eje, serie, titulo_sub in pares:
    barras = eje.bar(
        serie.index,
        serie.values,
        color=PALETA_COLORES[:len(serie)],
        edgecolor="white",
        width=0.5
    )
    valor_maximo = serie.max()
    for barra in barras:
        altura = barra.get_height()
        if titulo_sub == "Cantidad de ítems":
            etiqueta_encima = str(int(altura))
        else:
            etiqueta_encima = f"${altura / 1e3:.0f}K"
        eje.text(
            barra.get_x() + barra.get_width() / 2,
            altura + valor_maximo * 0.02,
            etiqueta_encima,
            ha="center", va="bottom", fontsize=9
        )
    eje.set_title(titulo_sub, fontsize=9)
    if titulo_sub != "Cantidad de ítems":
        eje.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda v, _: f"${v / 1e3:.0f}K")
        )
    eje.grid(axis="y", linestyle="--", alpha=0.4)
    eje.tick_params(axis="x", labelsize=9)

plt.tight_layout()
ruta_salida = carpeta_graficos / "05_medio_transporte.png"
plt.savefig(ruta_salida, bbox_inches="tight")
plt.show()
print(f"✔ Gráfico 5 guardado: {ruta_salida.name}")


# =======================================================================
# GRÁFICO 6 – Régimen aduanero: cantidad de despachos
# =======================================================================
figura, eje = plt.subplots(figsize=(10, 4))
figura.suptitle(
    "Distribución por Régimen Aduanero\nFebrero 2026",
    fontsize=13, fontweight="bold"
)

cantidad_por_regimen = datos["REGIMEN"].value_counts().sort_values()

# Acortamos etiquetas largas y asignamos color según si es exportación o importación
etiquetas_regimen = [
    nombre[:50] + "…" if len(nombre) > 50 else nombre
    for nombre in cantidad_por_regimen.index
]
colores_regimen = [
    COLOR_EXPORTACION if "EXPORT" in nombre else COLOR_IMPORTACION
    for nombre in cantidad_por_regimen.index
]

barras = eje.barh(
    etiquetas_regimen,
    cantidad_por_regimen.values,
    color=colores_regimen,
    edgecolor="white",
    height=0.6
)
for barra in barras:
    ancho = barra.get_width()
    eje.text(
        ancho + 0.1,
        barra.get_y() + barra.get_height() / 2,
        str(int(ancho)),
        va="center", fontsize=9
    )

eje.set_xlabel("Cantidad de ítems", fontsize=9)
eje.tick_params(axis="y", labelsize=8.5)
eje.grid(axis="x", linestyle="--", alpha=0.4)

# Leyenda manual con parches de color
leyenda = [
    mpatches.Patch(color=COLOR_EXPORTACION, label="Exportación"),
    mpatches.Patch(color=COLOR_IMPORTACION, label="Importación"),
]
eje.legend(handles=leyenda, fontsize=9, loc="lower right")

plt.tight_layout()
ruta_salida = carpeta_graficos / "06_regimen_aduanero.png"
plt.savefig(ruta_salida, bbox_inches="tight")
plt.show()
print(f"✔ Gráfico 6 guardado: {ruta_salida.name}")


# =======================================================================
# GRÁFICO 7 – Composición de tributos en importaciones
# =======================================================================
# Filtramos solo las importaciones
solo_importaciones = datos[datos["OPERACION"] == "IMPORTACION"].copy()

# Sumamos cada tipo de tributo
tributos = {
    "Derecho": solo_importaciones["DERECHO"].sum(),
    "IVA":     solo_importaciones["IVA"].sum(),
    "ISC":     solo_importaciones["ISC"].sum(),
    "Renta":   solo_importaciones["RENTA"].sum(),
    "Otros":   solo_importaciones["OTROS"].sum(),
}
# Quitamos los que son cero (no aplican en este período)
tributos = {nombre: monto for nombre, monto in tributos.items() if monto > 0}

figura, eje = plt.subplots(figsize=(7, 5))
figura.suptitle(
    "Composición Tributaria – Importaciones\nFebrero 2026",
    fontsize=13, fontweight="bold"
)

sectores, textos, porcentajes = eje.pie(
    list(tributos.values()),
    labels=list(tributos.keys()),
    autopct="%1.1f%%",
    colors=PALETA_COLORES[:len(tributos)],
    startangle=140,
    wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    textprops={"fontsize": 10},
)
for texto_pct in porcentajes:
    texto_pct.set_fontsize(9)
    texto_pct.set_fontweight("bold")

# Mostramos el total recaudado debajo del gráfico
total_recaudado = sum(tributos.values())
eje.text(
    0, -1.45,
    f"Total recaudado: Gs {total_recaudado:,.0f}",
    ha="center", fontsize=9, color="#444444"
)

plt.tight_layout()
ruta_salida = carpeta_graficos / "07_composicion_tributaria.png"
plt.savefig(ruta_salida, bbox_inches="tight")
plt.show()
print(f"✔ Gráfico 7 guardado: {ruta_salida.name}")


# =======================================================================
# GRÁFICO 8 – Dispersión: Kilo Neto vs FOB USD por operación
# =======================================================================
figura, eje = plt.subplots(figsize=(9, 5))
figura.suptitle(
    "Relación: Kilo Neto vs FOB USD por Operación\nFebrero 2026",
    fontsize=13, fontweight="bold"
)

# Graficamos cada tipo de operación en un color distinto
operaciones_disponibles = [
    ("EXPORTACION", COLOR_EXPORTACION),
    ("IMPORTACION", COLOR_IMPORTACION),
]
for nombre_op, color in operaciones_disponibles:
    subset = datos[datos["OPERACION"] == nombre_op]
    eje.scatter(
        subset["KILO NETO"],
        subset["FOB DOLAR"],
        label=nombre_op,
        color=color,
        alpha=0.75,
        s=60,
        edgecolors="white",
        linewidths=0.5
    )

eje.set_xlabel("Kilo Neto (kg)", fontsize=9)
eje.set_ylabel("FOB (USD)", fontsize=9)
eje.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v / 1e3:.0f}K"))
eje.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v / 1e3:.0f}K"))
eje.legend(fontsize=9)
eje.grid(linestyle="--", alpha=0.4)

plt.tight_layout()
ruta_salida = carpeta_graficos / "08_kilo_vs_fob.png"
plt.savefig(ruta_salida, bbox_inches="tight")
plt.show()
print(f"✔ Gráfico 8 guardado: {ruta_salida.name}")


# ── 5. RESUMEN ESTADÍSTICO FINAL ──────────────────────────────────────────
total_exportaciones = (datos["OPERACION"] == "EXPORTACION").sum()
total_importaciones = (datos["OPERACION"] == "IMPORTACION").sum()
fob_exportaciones   = datos[datos["OPERACION"] == "EXPORTACION"]["FOB DOLAR"].sum()
fob_importaciones   = datos[datos["OPERACION"] == "IMPORTACION"]["FOB DOLAR"].sum()

print()
print("=" * 55)
print("  RESUMEN GENERAL – Febrero 2026")
print("=" * 55)
print(f"  Total de ítems     : {cantidad_registros}")
print(f"  Exportaciones      : {total_exportaciones}")
print(f"  Importaciones      : {total_importaciones}")
print(f"  FOB total (USD)    : ${datos['FOB DOLAR'].sum():,.2f}")
print(f"  FOB Export (USD)   : ${fob_exportaciones:,.2f}")
print(f"  FOB Import (USD)   : ${fob_importaciones:,.2f}")
print(f"  Imponible (Gs)     : {datos['IMPONIBLE GS'].sum():,.0f}")
print(f"  Kilo neto total    : {datos['KILO NETO'].sum():,.2f} kg")
print(f"  Gráficos guardados : {carpeta_graficos}")
print("=" * 55)
