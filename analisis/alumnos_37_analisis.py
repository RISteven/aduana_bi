"""
==============================================================================
37 ANÁLISIS ÚNICOS DE DATOS ADUANEROS – EJERCICIOS POR ALUMNO
Comercio Exterior de Paraguay – Capa Silver del DWH
==============================================================================
Ninguno de los 37 análisis repite los 30 gráficos avanzados de clase.

Ejecutar un alumno específico:
  python analisis/alumnos_37_analisis.py A01

Ejecutar todos:
  python analisis/alumnos_37_analisis.py

Librerías:
  pip install duckdb pandas numpy matplotlib seaborn scipy
==============================================================================
"""

import sys
import duckdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path

np.random.seed(42)

# ─────────────────────────────────────────────────────────────
# RUTAS Y CONFIGURACIÓN GLOBAL
# ─────────────────────────────────────────────────────────────
RAIZ        = Path(__file__).parent.parent
PARQUET     = RAIZ / "data_lake" / "silver" / "aduana_item_clean.parquet"
SALIDA      = Path(__file__).parent / "graficos" / "alumnos"
SALIDA.mkdir(parents=True, exist_ok=True)

VERDE   = "#016948"
ROJO    = "#B44365"
AZUL    = "#012169"
NARANJA = "#E8A838"
PALETA  = ["#012169","#D4285B","#009EFF","#259B9A",
           "#6CACE4","#7B2A8D","#E8A838","#4A4A4A",
           "#2E8B57","#DC143C","#4B0082","#AAAAAA"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 120, "axes.titlesize": 11, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 8,
})

# ─────────────────────────────────────────────────────────────
# CARGA DE DATOS (una sola vez para todos los análisis)
# ─────────────────────────────────────────────────────────────
con   = duckdb.connect()
datos = con.execute(f"SELECT * FROM '{PARQUET}'").fetchdf()

for c in ["DERECHO","IVA","ISC","RENTA","OTROS","TOTAL","SERVICIO","COTIZACION",
          "AJUSTE A INCLUIR","AJUSTE A DEDUCIR"]:
    datos[c] = pd.to_numeric(datos[c], errors="coerce").fillna(0)

datos["DIAS_DESPACHO"] = (datos["CANCELACION"] - datos["OFICIALIZACION"]).dt.days
datos["PRECIO_USD_KG"] = datos["FOB DOLAR"] / datos["KILO NETO"].replace(0, np.nan)
datos["MERMA_PCT"]     = (datos["KILO BRUTO"] - datos["KILO NETO"]) / datos["KILO NETO"].replace(0, np.nan) * 100
datos["CIF_DOLAR"]     = datos["FOB DOLAR"] + datos["FLETE DOLAR"] + datos["SEGURO DOLAR"]
datos["SEGURO_PCT_CIF"]= datos["SEGURO DOLAR"] / datos["CIF_DOLAR"].replace(0, np.nan) * 100
datos["FLETE_USD_KG"]  = datos["FLETE DOLAR"] / datos["KILO NETO"].replace(0, np.nan)
datos["TASA_TRIB_PCT"] = datos["TOTAL"] / datos["IMPONIBLE GS"].replace(0, np.nan) * 100
datos["CAP_ARANC"]     = datos["POSICION"].astype(str).str[:2]
datos["AJUSTE_NETO"]   = datos["AJUSTE A INCLUIR"] - datos["AJUSTE A DEDUCIR"]
datos["IVA_PCT_FOB"]   = datos["IVA"] / datos["IMPONIBLE GS"].replace(0, np.nan) * 100

exp = datos[datos["OPERACION"] == "EXPORTACION"].copy()
imp = datos[datos["OPERACION"] == "IMPORTACION"].copy()
print(f"✔ Datos: {len(datos)} registros  (Exp:{len(exp)} | Imp:{len(imp)})")


def guardar(nombre: str) -> None:
    ruta = SALIDA / nombre
    plt.savefig(ruta, bbox_inches="tight")
    plt.close("all")
    print(f"  ✔  {ruta.name}")


CATALOGO = {
    "A01": "Canal Verde vs Naranja – tiempos y distribución de operaciones",
    "A02": "Ratio de embalaje (Kilo Bruto vs Neto) por rubro",
    "A03": "Impacto de acuerdos comerciales en el valor FOB",
    "A04": "Composición CIF: FOB + Flete + Seguro por operación",
    "A05": "Seguro como porcentaje del CIF por medio de transporte",
    "A06": "Mercancías NUEVAS vs USADAS: FOB, volumen y precio",
    "A07": "Top capítulos arancelarios por FOB de exportación",
    "A08": "Tasa de flete por kilogramo según medio de transporte",
    "A09": "Mapa de calor Rubro × Aduana (FOB total)",
    "A10": "Densidad de valor USD/kg comparada por aduana",
    "A11": "Matriz de flujos País de Origen → País de Destino",
    "A12": "Top 10 rubros de EXPORTACIÓN por valor FOB",
    "A13": "Distribución de unidades de medida estadística",
    "A14": "Volatilidad del tipo de cambio Gs/USD por despacho",
    "A15": "Mapa de calor Rubro × Medio de Transporte",
    "A16": "FOB y frecuencia por código de destinación aduanera",
    "A17": "Tiempo de despacho por Canal y Aduana (heatmap)",
    "A18": "Tasa efectiva de IVA cobrado vs valor imponible por régimen",
    "A19": "Carga tributaria en Guaraníes desagregada por régimen",
    "A20": "Top marcas de ítems por frecuencia y FOB promedio",
    "A21": "Relación Seguro vs Flete por despacho y operación",
    "A22": "Valor imponible vs FOB: análisis del ajuste aduanero",
    "A23": "Productividad por aduana: FOB promedio por despacho",
    "A24": "Ranking de capítulos arancelarios con nombre completo",
    "A25": "Precio USD/kg en mercancías NUEVAS vs USADAS por rubro",
    "A26": "Participación de países de ORIGEN en importaciones",
    "A27": "Coeficiente de variación del precio USD/kg por rubro",
    "A28": "Perfil radar multi-dimensional por aduana",
    "A29": "Distribución de ítems por despacho (histograma + CDF)",
    "A30": "Tasa tributaria efectiva (%) por régimen aduanero",
    "A31": "Kilo Bruto vs Kilo Neto: dispersión y línea de igualdad",
    "A32": "FOB por acuerdo comercial desglosado por tipo de operación",
    "A33": "Concentración de FOB por aduana dentro de cada operación",
    "A34": "Mapa de calor Acuerdo Comercial × País Destino (FOB)",
    "A35": "Ajustes aduaneros: impacto en el valor declarado",
    "A36": "Perfil araña exportación vs importación (6 métricas)",
    "A37": "Dashboard integrado DWH: 4 análisis simultáneos",
}


# ===========================================================================
# A01 – CANAL VERDE vs NARANJA
# Enseña: el canal de control (V=automático, N=revisión documental) afecta
# los tiempos de despacho y se distribuye distinto según la operación.
# Datos: REALES (columna CANAL).
# ===========================================================================
def analisis_A01():
    print("\n[A01] Canal Verde vs Naranja")
    canal_label = {"V": "Verde (automático)", "N": "Naranja (revisión)"}

    tabla = datos.groupby(["CANAL", "OPERACION"]).size().unstack(fill_value=0)
    canales = tabla.index.tolist()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Canal de Control Aduanero: Verde vs Naranja (Feb 2026)",
                 fontsize=12, fontweight="bold")

    x = np.arange(len(canales))
    ancho = 0.35
    for i, (col, color) in enumerate(zip(tabla.columns, [VERDE, ROJO])):
        bs = ax1.bar(x + i*ancho, tabla[col], ancho, label=col,
                     color=color, edgecolor="white", alpha=0.85)
        for b in bs:
            ax1.text(b.get_x()+b.get_width()/2, b.get_height()+0.1,
                     str(int(b.get_height())), ha="center", fontsize=9)
    ax1.set_xticks(x + ancho/2)
    ax1.set_xticklabels([canal_label.get(c, c) for c in canales])
    ax1.set_ylabel("Cantidad de despachos")
    ax1.set_title("Despachos por canal y tipo de operación")
    ax1.legend(title="Operación")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    grupos = [datos[datos["CANAL"] == c]["DIAS_DESPACHO"].dropna().values
              for c in canales]
    etiq = [canal_label.get(c, c) for c in canales]
    colores_c = [VERDE, NARANJA][:len(canales)]
    bp = ax2.boxplot(grupos, tick_labels=etiq, patch_artist=True,
                     medianprops={"color":"white","linewidth":2},
                     flierprops={"marker":"o","markersize":5,"alpha":0.6})
    for p, c in zip(bp["boxes"], colores_c):
        p.set_facecolor(c); p.set_alpha(0.8)
    for i, (g, c) in enumerate(zip(grupos, colores_c)):
        if len(g) > 0:
            ax2.text(i+1, np.mean(g)+0.2, f"x̄={np.mean(g):.1f}d",
                     ha="center", fontsize=8, color=c)
    ax2.set_ylabel("Días de despacho")
    ax2.set_title("Tiempo de despacho según canal de control")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A01_canal_verde_naranja.png")


# ===========================================================================
# A02 – RATIO DE EMBALAJE (KILO BRUTO vs NETO)
# Enseña: la diferencia entre kilo bruto y neto revela el peso del embalaje.
# Un ratio alto puede indicar embalaje costoso o mercancías frágiles.
# Datos: REALES.
# ===========================================================================
def analisis_A02():
    print("\n[A02] Ratio de embalaje por rubro")
    d = datos[datos["MERMA_PCT"].notna() & (datos["MERMA_PCT"] < 50) &
              (datos["KILO NETO"] > 0)].copy()

    prom_merma = d.groupby("RUBRO")["MERMA_PCT"].mean().sort_values(ascending=False)
    etiq = [r[:35]+"…" if len(r)>35 else r for r in prom_merma.index]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Análisis de Embalaje: Diferencia Kilo Bruto vs Neto (Feb 2026)",
                 fontsize=12, fontweight="bold")

    colores_bar = PALETA[:len(prom_merma)]
    ax1.barh(etiq, prom_merma.values, color=colores_bar, edgecolor="white", height=0.6)
    for i, v in enumerate(prom_merma.values):
        ax1.text(v + 0.05, i, f"{v:.2f}%", va="center", fontsize=8)
    ax1.set_xlabel("Ratio embalaje promedio (%)")
    ax1.set_title("% promedio de embalaje por rubro\n[(Bruto–Neto)/Neto × 100]")
    ax1.grid(axis="x", linestyle="--", alpha=0.4)

    ax2.scatter(d["KILO NETO"], d["KILO BRUTO"],
                c=[PALETA[i % len(PALETA)] for i in range(len(d))],
                s=80, alpha=0.8, edgecolors="white", linewidths=0.8)
    lim = max(d["KILO BRUTO"].max(), d["KILO NETO"].max()) * 1.05
    ax2.plot([0, lim], [0, lim], color="#aaa", linestyle="--",
             linewidth=1.5, label="Bruto = Neto (sin embalaje)")
    ax2.set_xlabel("Kilo Neto (kg)")
    ax2.set_ylabel("Kilo Bruto (kg)")
    ax2.set_title("Kilo Bruto vs Kilo Neto por despacho")
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v/1e3:.0f}K"))
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v/1e3:.0f}K"))
    ax2.legend()
    ax2.grid(linestyle="--", alpha=0.35)

    plt.tight_layout()
    guardar("A02_ratio_embalaje.png")


# ===========================================================================
# A03 – ACUERDOS COMERCIALES
# Enseña: los acuerdos (MERCOSUR, AAP.CE 74, SIN ACUERDO) pueden generar
# preferencias arancelarias y aumentar el volumen exportado/importado.
# Datos: REALES.
# ===========================================================================
def analisis_A03():
    print("\n[A03] Acuerdos comerciales")
    fob_acuerdo = datos.groupby("ACUERDO")["FOB DOLAR"].sum().sort_values(ascending=False)
    cnt_acuerdo = datos.groupby("ACUERDO")["FOB DOLAR"].count()

    tabla = datos.groupby(["ACUERDO","OPERACION"])["FOB DOLAR"].sum().unstack(fill_value=0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Impacto de Acuerdos Comerciales en el FOB (Feb 2026)",
                 fontsize=12, fontweight="bold")

    cunas, _, pcts = ax1.pie(fob_acuerdo.values, labels=fob_acuerdo.index,
                              autopct="%1.1f%%", colors=PALETA[:len(fob_acuerdo)],
                              startangle=90, wedgeprops={"edgecolor":"white","linewidth":1.5},
                              pctdistance=0.75)
    for p in pcts:
        p.set_fontsize(9); p.set_fontweight("bold"); p.set_color("white")
    ax1.set_title("Participación de acuerdos por FOB total")
    ax1.text(0, -1.35, f"Total: ${fob_acuerdo.sum():,.0f} USD",
             ha="center", fontsize=9, color="#444")

    x = np.arange(len(tabla.index))
    ancho = 0.35
    for i, (col, color) in enumerate(zip(tabla.columns, [VERDE, ROJO])):
        bs = ax2.bar(x + i*ancho, tabla[col]/1e3, ancho, label=col,
                     color=color, edgecolor="white", alpha=0.85)
        for b in bs:
            if b.get_height() > 0:
                ax2.text(b.get_x()+b.get_width()/2, b.get_height()+0.5,
                         f"${b.get_height():.0f}K", ha="center", fontsize=7.5)
    ax2.set_xticks(x + ancho/2)
    ax2.set_xticklabels(tabla.index, rotation=15, ha="right")
    ax2.set_ylabel("FOB (USD miles)")
    ax2.set_title("FOB por acuerdo y tipo de operación")
    ax2.legend(title="Operación")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A03_acuerdos_comerciales.png")


# ===========================================================================
# A04 – COMPOSICIÓN CIF (FOB + FLETE + SEGURO)
# Enseña: el valor CIF es la base imponible en importaciones.
# Descomponer sus componentes muestra la estructura del costo internacional.
# Datos: REALES.
# ===========================================================================
def analisis_A04():
    print("\n[A04] Composición CIF")
    res = datos.groupby("OPERACION").agg(
        FOB=("FOB DOLAR","sum"),
        FLETE=("FLETE DOLAR","sum"),
        SEGURO=("SEGURO DOLAR","sum")
    ).reset_index()

    operaciones = res["OPERACION"].tolist()
    x = np.arange(len(operaciones))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Composición del Valor CIF por Tipo de Operación (Feb 2026)",
                 fontsize=12, fontweight="bold")

    base = np.zeros(len(operaciones))
    componentes = [("FOB", AZUL), ("FLETE", NARANJA), ("SEGURO", ROJO)]
    for comp, color in componentes:
        vals = res[comp].values / 1e3
        ax1.bar(operaciones, vals, bottom=base/1e3, label=comp,
                color=color, edgecolor="white", alpha=0.85)
        for i, (v, b) in enumerate(zip(vals, base/1e3)):
            if v > 0:
                ax1.text(i, b + v/2, f"${v:.0f}K", ha="center", fontsize=8, color="white")
        base += res[comp].values
    ax1.set_ylabel("Monto (USD miles)")
    ax1.set_title("Monto CIF apilado: FOB + Flete + Seguro")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for i, (_, fila) in enumerate(res.iterrows()):
        total = fila["FOB"] + fila["FLETE"] + fila["SEGURO"]
        if total == 0: continue
        tamaños = [fila["FOB"]/total*100, fila["FLETE"]/total*100, fila["SEGURO"]/total*100]
        labels  = [f"FOB\n{tamaños[0]:.1f}%", f"Flete\n{tamaños[1]:.1f}%",
                   f"Seguro\n{tamaños[2]:.1f}%"]
        ax2.pie(tamaños, labels=labels, colors=[AZUL, NARANJA, ROJO],
                startangle=90 + i*180,
                wedgeprops={"edgecolor":"white","linewidth":1.5},
                radius=0.5 - i*0.05,
                center=(i*1.2, 0))
        ax2.text(i*1.2, -0.65, fila["OPERACION"][:3].title(),
                 ha="center", fontsize=9, fontweight="bold")
    ax2.set_xlim(-0.7, 1.9)
    ax2.set_ylim(-0.8, 0.8)
    ax2.set_title("Proporción CIF por operación")
    ax2.axis("equal")

    plt.tight_layout()
    guardar("A04_composicion_cif.png")


# ===========================================================================
# A05 – SEGURO COMO % DEL CIF
# Enseña: el costo del seguro varía según el medio de transporte y el riesgo
# de la ruta. El flete aéreo suele incluir mayor cobertura.
# Datos: REALES.
# ===========================================================================
def analisis_A05():
    print("\n[A05] Seguro como % del CIF por transporte")
    d = datos[datos["CIF_DOLAR"] > 0].copy()

    prom_seg = d.groupby("MEDIO TRANSPORTE")["SEGURO_PCT_CIF"].mean().sort_values(ascending=False)
    grupos_seg = [d[d["MEDIO TRANSPORTE"]==t]["SEGURO_PCT_CIF"].dropna().values
                  for t in prom_seg.index]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Seguro como % del Valor CIF por Medio de Transporte (Feb 2026)",
                 fontsize=12, fontweight="bold")

    colores_t = PALETA[:len(prom_seg)]
    bs = ax1.bar(prom_seg.index, prom_seg.values, color=colores_t, edgecolor="white", width=0.55)
    for b, v in zip(bs, prom_seg.values):
        ax1.text(b.get_x()+b.get_width()/2, v+0.01, f"{v:.3f}%", ha="center", fontsize=9)
    ax1.set_ylabel("Seguro / CIF (%)")
    ax1.set_title("Porcentaje promedio de seguro\nsobre el valor CIF")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    bp = ax2.boxplot(grupos_seg, tick_labels=prom_seg.index, patch_artist=True,
                     medianprops={"color":"white","linewidth":2},
                     flierprops={"marker":"o","markersize":5,"alpha":0.6})
    for p, c in zip(bp["boxes"], colores_t):
        p.set_facecolor(c); p.set_alpha(0.8)
    ax2.set_ylabel("Seguro / CIF (%)")
    ax2.set_title("Distribución del porcentaje de seguro\npor medio de transporte")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A05_seguro_pct_cif.png")


# ===========================================================================
# A06 – MERCANCÍAS NUEVAS vs USADAS
# Enseña: comparar si las importaciones de bienes usados tienen menor valor
# unitario (USD/kg) y cómo se distribuyen por tipo de operación.
# Datos: REALES (columna USO).
# ===========================================================================
def analisis_A06():
    print("\n[A06] Nuevo vs Usado")
    tabla = datos.groupby(["USO","OPERACION"]).agg(
        cantidad=("FOB DOLAR","count"),
        fob=("FOB DOLAR","sum"),
        precio_kg=("PRECIO_USD_KG","mean")
    ).reset_index()

    usos = datos["USO"].dropna().unique()
    metricas = ["cantidad","fob","precio_kg"]
    titulos  = ["Cantidad de despachos","FOB total (USD)","Precio promedio (USD/kg)"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Mercancías NUEVAS vs USADAS – Comparativa (Feb 2026)",
                 fontsize=12, fontweight="bold")

    for ax, metrica, titulo in zip(axes, metricas, titulos):
        sub = tabla.pivot(index="USO", columns="OPERACION", values=metrica).fillna(0)
        x = np.arange(len(sub.index))
        ancho = 0.35
        for i, (col, color) in enumerate(zip(sub.columns, [VERDE, ROJO])):
            bs = ax.bar(x + i*ancho, sub[col], ancho, label=col,
                        color=color, edgecolor="white", alpha=0.85)
            for b in bs:
                if b.get_height() > 0:
                    ax.text(b.get_x()+b.get_width()/2, b.get_height()*1.02,
                            f"{b.get_height():.1f}", ha="center", fontsize=7.5)
        ax.set_xticks(x + ancho/2)
        ax.set_xticklabels(sub.index)
        ax.set_title(titulo)
        ax.legend(title="Operación")
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A06_nuevo_vs_usado.png")


# ===========================================================================
# A07 – TOP CAPÍTULOS ARANCELARIOS POR FOB DE EXPORTACIÓN
# Enseña: los capítulos arancelarios (2 primeros dígitos de la posición)
# agrupan grandes categorías de mercancías según el Arancel Nacional.
# Datos: REALES.
# ===========================================================================
def analisis_A07():
    print("\n[A07] Top capítulos arancelarios (exportación)")
    fob_cap = exp.groupby("CAP_ARANC")["FOB DOLAR"].sum().sort_values(ascending=True)
    # Añadir descripción resumida del capítulo
    desc_cap = exp.groupby("CAP_ARANC")["DESC CAPITULO"].first()
    etiq = [f"Cap. {c} – {desc_cap.get(c,'')[:30]}…" if len(desc_cap.get(c,''))>30
            else f"Cap. {c} – {desc_cap.get(c,'')}" for c in fob_cap.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Top Capítulos Arancelarios por FOB Exportado (Feb 2026)",
                 fontsize=12, fontweight="bold")
    colores = PALETA[:len(fob_cap)]
    barras = ax.barh(etiq, fob_cap.values, color=colores, edgecolor="white", height=0.65)
    for b in barras:
        ax.text(b.get_width()*1.01, b.get_y()+b.get_height()/2,
                f"${b.get_width():,.0f}", va="center", fontsize=8)
    ax.set_xlabel("FOB (USD)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v/1e3:.0f}K"))
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    guardar("A07_capitulos_arancel_exp.png")


# ===========================================================================
# A08 – TASA DE FLETE POR KILOGRAMO
# Enseña: el costo del flete por kg varía enormemente según el medio de
# transporte. El flete aéreo puede ser 10x más caro que el marítimo.
# Datos: REALES.
# ===========================================================================
def analisis_A08():
    print("\n[A08] Tasa de flete por kg según transporte")
    d = datos[(datos["FLETE_USD_KG"].notna()) & (datos["FLETE_USD_KG"] > 0) &
              (datos["FLETE_USD_KG"] < 50)].copy()

    prom_ft = d.groupby("MEDIO TRANSPORTE")["FLETE_USD_KG"].mean().sort_values(ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Tasa de Flete por Kilogramo según Medio de Transporte (Feb 2026)",
                 fontsize=12, fontweight="bold")

    colores_t = PALETA[:len(prom_ft)]
    bs = ax1.bar(prom_ft.index, prom_ft.values, color=colores_t, edgecolor="white", width=0.55)
    for b, v in zip(bs, prom_ft.values):
        ax1.text(b.get_x()+b.get_width()/2, v+0.01, f"${v:.3f}/kg", ha="center", fontsize=9)
    ax1.set_ylabel("USD / Kilo Neto")
    ax1.set_title("Flete promedio por kilogramo")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for transp, color in zip(d["MEDIO TRANSPORTE"].unique(), PALETA):
        sub = d[d["MEDIO TRANSPORTE"]==transp]
        ax2.scatter(sub["KILO NETO"], sub["FLETE DOLAR"],
                    label=transp, color=color, s=70, alpha=0.75,
                    edgecolors="white", linewidths=0.8, zorder=3)
    ax2.set_xlabel("Kilo Neto (kg)")
    ax2.set_ylabel("Flete (USD)")
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"{v/1e3:.0f}K"))
    ax2.set_title("Kilo Neto vs Flete por medio de transporte")
    ax2.legend()
    ax2.grid(linestyle="--", alpha=0.35)

    plt.tight_layout()
    guardar("A08_flete_por_kg.png")


# ===========================================================================
# A09 – MAPA DE CALOR RUBRO × ADUANA
# Enseña: qué rubros de mercancías ingresan o salen por cada aduana.
# Algunas aduanas son especializadas (ej. aeropuerto = mercancías de alto valor).
# Datos: REALES.
# ===========================================================================
def analisis_A09():
    print("\n[A09] Heatmap Rubro × Aduana")
    pivot = (datos.groupby(["RUBRO","ADUANA"])["FOB DOLAR"].sum()
             .unstack(fill_value=0))
    # Abreviar nombres de rubro para visualización
    pivot.index = [r[:30]+"…" if len(r)>30 else r for r in pivot.index]

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.suptitle("Mapa de Calor: FOB por Rubro y Aduana (Feb 2026)",
                 fontsize=12, fontweight="bold")
    sns.heatmap(pivot/1e3, ax=ax, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, cbar_kws={"label":"FOB (USD miles)"})
    ax.set_xlabel("Aduana")
    ax.set_ylabel("Rubro")
    ax.set_title("Valores en USD miles (0 = sin operaciones en esa combinación)", fontsize=8)
    plt.tight_layout()
    guardar("A09_heatmap_rubro_aduana.png")


# ===========================================================================
# A10 – DENSIDAD DE VALOR (USD/KG) POR ADUANA
# Enseña: las aduanas con mayor precio por kg manejan mercancías de mayor
# valor agregado (electrónica, farmacéuticos, etc.).
# Datos: REALES.
# ===========================================================================
def analisis_A10():
    print("\n[A10] Densidad de valor USD/kg por aduana")
    d = datos[datos["PRECIO_USD_KG"].notna() & (datos["PRECIO_USD_KG"] < 500)].copy()
    aduanas = d.groupby("ADUANA")["PRECIO_USD_KG"].mean().sort_values(ascending=False).index

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Densidad de Valor (USD/kg) por Aduana (Feb 2026)",
                 fontsize=12, fontweight="bold")

    prom = d.groupby("ADUANA")["PRECIO_USD_KG"].mean().reindex(aduanas)
    colores_a = PALETA[:len(aduanas)]
    bs = ax1.bar(aduanas, prom.values, color=colores_a, edgecolor="white", width=0.6)
    for b, v in zip(bs, prom.values):
        ax1.text(b.get_x()+b.get_width()/2, v+0.5, f"${v:.1f}", ha="center", fontsize=9)
    ax1.set_ylabel("Precio promedio (USD/kg)")
    ax1.set_title("Precio promedio USD/kg por aduana")
    ax1.tick_params(axis="x", rotation=20, labelsize=8)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    grupos = [d[d["ADUANA"]==a]["PRECIO_USD_KG"].values for a in aduanas]
    bp = ax2.boxplot(grupos, tick_labels=list(aduanas), patch_artist=True,
                     medianprops={"color":"white","linewidth":2},
                     flierprops={"marker":"o","markersize":5,"alpha":0.6})
    for p, c in zip(bp["boxes"], colores_a):
        p.set_facecolor(c); p.set_alpha(0.8)
    ax2.set_ylabel("USD/kg")
    ax2.set_title("Distribución de precio USD/kg por aduana")
    ax2.tick_params(axis="x", rotation=20, labelsize=8)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A10_densidad_valor_aduana.png")


# ===========================================================================
# A11 – MATRIZ DE FLUJOS PAÍS ORIGEN → PAÍS DESTINO
# Enseña: visualiza qué países abastecen a Paraguay (origen de importaciones)
# y hacia qué países exporta, revelando la red de socios comerciales.
# Datos: REALES.
# ===========================================================================
def analisis_A11():
    print("\n[A11] Matriz flujos País Origen → País Destino")
    pivot = (datos.groupby(["PAIS_ORIGEN_DESC","PAIS_DEST_DESC"])["FOB DOLAR"]
             .sum().unstack(fill_value=0))
    pivot.index   = [p[:12]+"…" if len(p)>12 else p for p in pivot.index]
    pivot.columns = [p[:12]+"…" if len(p)>12 else p for p in pivot.columns]

    fig, ax = plt.subplots(figsize=(11, 7))
    fig.suptitle("Matriz de Flujos Comerciales: País Origen → País Destino (Feb 2026)",
                 fontsize=12, fontweight="bold")
    sns.heatmap(pivot/1e3, ax=ax, annot=True, fmt=".0f", cmap="Blues",
                linewidths=0.5, cbar_kws={"label":"FOB (USD miles)"})
    ax.set_xlabel("País de Destino")
    ax.set_ylabel("País de Origen")
    ax.set_title("Cada celda = FOB total de esa ruta (USD miles)", fontsize=8)
    plt.tight_layout()
    guardar("A11_matriz_flujos_paises.png")


# ===========================================================================
# A12 – TOP 10 RUBROS DE EXPORTACIÓN POR FOB
# Enseña: a diferencia del G02 (importaciones), aquí vemos los rubros que
# Paraguay exporta. Oleaginosas y textiles dominan la balanza exportadora.
# Datos: REALES.
# ===========================================================================
def analisis_A12():
    print("\n[A12] Top 10 rubros de exportación")
    fob_exp = (exp.groupby("RUBRO")["FOB DOLAR"].sum()
               .sort_values(ascending=True).tail(10))
    etiq = [r[:40]+"…" if len(r)>40 else r for r in fob_exp.index]
    total = fob_exp.sum()
    pcts  = fob_exp.values / total * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Top Rubros de EXPORTACIÓN por Valor FOB (Feb 2026)",
                 fontsize=12, fontweight="bold")
    barras = ax.barh(etiq, fob_exp.values, color=PALETA[:len(fob_exp)],
                     edgecolor="white", height=0.65)
    for b, pct in zip(barras, pcts):
        ax.text(b.get_width()*1.01, b.get_y()+b.get_height()/2,
                f"${b.get_width():,.0f}  ({pct:.1f}%)", va="center", fontsize=8)
    ax.set_xlabel("FOB (USD)")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f"${v/1e3:.0f}K"))
    ax.text(0.98, 0.02, f"Total exp: ${total:,.0f}",
            transform=ax.transAxes, ha="right", fontsize=9, color="#444")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    guardar("A12_top10_rubros_exportacion.png")


# ===========================================================================
# A13 – DISTRIBUCIÓN DE UNIDADES DE MEDIDA ESTADÍSTICA
# Enseña: cada mercancía se mide en su unidad natural (kg, unidades, litros…).
# La distribución revela si el comercio es en masa, piezas o volumen.
# Datos: REALES.
# ===========================================================================
def analisis_A13():
    print("\n[A13] Unidades de medida estadística")
    cnt_um = datos["UNIDAD MEDIDA ESTADISTICA"].value_counts()
    fob_um = datos.groupby("UNIDAD MEDIDA ESTADISTICA")["FOB DOLAR"].sum()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Distribución de Unidades de Medida Estadística (Feb 2026)",
                 fontsize=12, fontweight="bold")

    cunas, txts, pcts = ax1.pie(cnt_um.values, labels=cnt_um.index,
                                 autopct="%1.1f%%", colors=PALETA[:len(cnt_um)],
                                 startangle=90, wedgeprops={"edgecolor":"white","linewidth":1.5},
                                 pctdistance=0.75)
    for p in pcts:
        p.set_fontsize(9); p.set_fontweight("bold"); p.set_color("white")
    ax1.set_title("Por cantidad de despachos")

    x = np.arange(len(fob_um))
    bs = ax2.bar(fob_um.index, fob_um.values/1e3, color=PALETA[:len(fob_um)],
                 edgecolor="white", width=0.6)
    for b in bs:
        ax2.text(b.get_x()+b.get_width()/2, b.get_height()*1.02,
                 f"${b.get_height():.0f}K", ha="center", fontsize=9)
    ax2.set_ylabel("FOB (USD miles)")
    ax2.set_title("FOB total por unidad de medida")
    ax2.tick_params(axis="x", rotation=15)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A13_unidades_medida.png")


# ===========================================================================
# A14 – VOLATILIDAD DEL TIPO DE CAMBIO GS/USD
# Enseña: la cotización del guaraní frente al dólar varía entre despachos.
# Una alta dispersión aumenta el riesgo cambiario para exportadores/importadores.
# Datos: REALES (columna COTIZACION).
# ===========================================================================
def analisis_A14():
    print("\n[A14] Volatilidad del tipo de cambio Gs/USD")
    cotiz = datos["COTIZACION"].dropna()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Variación del Tipo de Cambio Gs/USD entre Despachos (Feb 2026)",
                 fontsize=12, fontweight="bold")

    ax1.hist(cotiz, bins=8, color=AZUL, edgecolor="white", alpha=0.85)
    ax1.axvline(cotiz.mean(), color=NARANJA, linestyle="--", linewidth=2,
                label=f"Promedio: {cotiz.mean():,.2f}")
    ax1.axvline(cotiz.median(), color=VERDE, linestyle="--", linewidth=2,
                label=f"Mediana:  {cotiz.median():,.2f}")
    ax1.set_xlabel("Cotización Gs/USD")
    ax1.set_ylabel("Frecuencia")
    ax1.set_title("Distribución del tipo de cambio por despacho")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    datos_sorted = datos.dropna(subset=["COTIZACION","FOB DOLAR"]).sort_values("COTIZACION")
    ax2.scatter(datos_sorted["COTIZACION"], datos_sorted["FOB DOLAR"]/1e3,
                c=np.where(datos_sorted["OPERACION"]=="EXPORTACION", VERDE, ROJO),
                s=70, alpha=0.8, edgecolors="white", linewidths=0.8)
    ax2.set_xlabel("Cotización Gs/USD")
    ax2.set_ylabel("FOB (USD miles)")
    ax2.set_title("Cotización vs FOB por despacho")
    ax2.grid(linestyle="--", alpha=0.35)
    leyenda = [mpatches.Patch(color=VERDE, label="Exportación"),
               mpatches.Patch(color=ROJO,  label="Importación")]
    ax2.legend(handles=leyenda)

    stats_box = (f"n = {len(cotiz)}\n"
                 f"Min: {cotiz.min():,.0f}\nMax: {cotiz.max():,.0f}\n"
                 f"CV: {cotiz.std()/cotiz.mean()*100:.2f}%")
    ax1.text(0.97, 0.97, stats_box, transform=ax1.transAxes, ha="right", va="top",
             fontsize=8, bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

    plt.tight_layout()
    guardar("A14_volatilidad_tipo_cambio.png")


# ===========================================================================
# A15 – MAPA DE CALOR RUBRO × MEDIO DE TRANSPORTE
# Enseña: ciertos rubros tienen preferencia logística clara (p.ej. granos
# van en buque/camión, farmacéuticos viajan en avión).
# Datos: REALES.
# ===========================================================================
def analisis_A15():
    print("\n[A15] Heatmap Rubro × Medio de Transporte")
    pivot = (datos.groupby(["RUBRO","MEDIO TRANSPORTE"])["FOB DOLAR"]
             .sum().unstack(fill_value=0))
    pivot.index = [r[:35]+"…" if len(r)>35 else r for r in pivot.index]

    fig, ax = plt.subplots(figsize=(10, 8))
    fig.suptitle("Mapa de Calor: FOB por Rubro y Medio de Transporte (Feb 2026)",
                 fontsize=12, fontweight="bold")
    sns.heatmap(pivot/1e3, ax=ax, annot=True, fmt=".0f", cmap="Greens",
                linewidths=0.5, cbar_kws={"label":"FOB (USD miles)"})
    ax.set_xlabel("Medio de Transporte")
    ax.set_ylabel("Rubro de Mercancía")
    plt.tight_layout()
    guardar("A15_heatmap_rubro_transporte.png")


# ===========================================================================
# A16 – FOB POR CÓDIGO DE DESTINACIÓN ADUANERA
# Enseña: cada destinación tiene un código que indica el régimen legal
# (EC01=Exportación a Consumo, IC04=Importación a Consumo, IT02=Temporaria…).
# Datos: REALES.
# ===========================================================================
def analisis_A16():
    print("\n[A16] FOB y frecuencia por destinación aduanera")
    res = datos.groupby("DESTINACION").agg(
        fob=("FOB DOLAR","sum"),
        cantidad=("FOB DOLAR","count")
    ).sort_values("fob", ascending=False)

    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.suptitle("FOB y Cantidad de Despachos por Código de Destinación (Feb 2026)",
                 fontsize=12, fontweight="bold")
    ax2 = ax1.twinx()

    x = np.arange(len(res))
    bs = ax1.bar(x, res["fob"]/1e3, color=AZUL, edgecolor="white", alpha=0.8,
                 label="FOB (USD miles)", width=0.5)
    ax2.plot(x, res["cantidad"], marker="D", color=NARANJA, linewidth=2,
             markersize=8, label="Cantidad despachos", zorder=5)

    for b, cnt in zip(bs, res["cantidad"]):
        ax1.text(b.get_x()+b.get_width()/2, b.get_height()*1.02,
                 f"${b.get_height():.0f}K", ha="center", fontsize=8, color=AZUL)
    for xi, cnt in zip(x, res["cantidad"]):
        ax2.text(xi, cnt+0.1, str(cnt), ha="center", fontsize=8, color=NARANJA)

    ax1.set_xticks(x)
    ax1.set_xticklabels(res.index)
    ax1.set_ylabel("FOB (USD miles)", color=AZUL)
    ax2.set_ylabel("Cantidad de despachos", color=NARANJA)
    ax1.set_title("Destinación: EC01=Exp.Consumo, IC04=Imp.Consumo, IT02=Imp.Temporaria,\n"
                  "EFC1=Exp.Comp., EM01=Exp.Maquila", fontsize=7.5)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    lineas1, lab1 = ax1.get_legend_handles_labels()
    lineas2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(lineas1+lineas2, lab1+lab2, loc="upper right", fontsize=8)

    plt.tight_layout()
    guardar("A16_fob_por_destinacion.png")


# ===========================================================================
# A17 – TIEMPO DE DESPACHO POR CANAL Y ADUANA
# Enseña: cruzar el canal de control con la aduana revela si ciertas aduanas
# son más eficientes en el canal verde que en el naranja.
# Datos: REALES.
# ===========================================================================
def analisis_A17():
    print("\n[A17] Heatmap tiempo despacho Canal × Aduana")
    pivot = (datos.groupby(["CANAL","ADUANA"])["DIAS_DESPACHO"]
             .mean().unstack(fill_value=np.nan))
    pivot.index = [{"V":"Verde (automático)","N":"Naranja (revisión)"}.get(c,c)
                   for c in pivot.index]

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.suptitle("Tiempo Promedio de Despacho (días) por Canal y Aduana (Feb 2026)",
                 fontsize=12, fontweight="bold")
    mask = pivot.isna()
    sns.heatmap(pivot, ax=ax, annot=True, fmt=".1f", cmap="RdYlGn_r",
                linewidths=0.5, mask=mask,
                cbar_kws={"label":"Días promedio de despacho"})
    ax.set_xlabel("Aduana")
    ax.set_ylabel("Canal de control")
    ax.set_title("Menor valor = despacho más rápido (verde=eficiente)", fontsize=8)
    plt.tight_layout()
    guardar("A17_heatmap_canal_aduana.png")


# ===========================================================================
# A18 – TASA EFECTIVA DE IVA POR RÉGIMEN
# Enseña: el IVA se aplica sobre el valor imponible; algunos regímenes
# especiales (maquila, temporaria) tienen tratamiento diferenciado.
# Datos: REALES.
# ===========================================================================
def analisis_A18():
    print("\n[A18] Tasa efectiva de IVA por régimen")
    d = datos[datos["IMPONIBLE GS"] > 0].copy()
    d["IVA_PCT"] = d["IVA"] / d["IMPONIBLE GS"] * 100
    tasa = d.groupby("REGIMEN")["IVA_PCT"].mean().sort_values(ascending=False)
    etiq = [r[:40]+"…" if len(r)>40 else r for r in tasa.index]

    monto = datos.groupby("REGIMEN")["IVA"].sum().reindex(tasa.index)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("IVA: Tasa Efectiva y Monto Total por Régimen Aduanero (Feb 2026)",
                 fontsize=12, fontweight="bold")

    colores_r = PALETA[:len(tasa)]
    bs = ax1.barh(etiq, tasa.values, color=colores_r, edgecolor="white", height=0.6)
    for b, v in zip(bs, tasa.values):
        ax1.text(v+0.1, b.get_y()+b.get_height()/2, f"{v:.2f}%", va="center", fontsize=8)
    ax1.set_xlabel("Tasa IVA efectiva (%)")
    ax1.set_title("Tasa promedio de IVA sobre Imponible Gs")
    ax1.grid(axis="x", linestyle="--", alpha=0.4)

    bs2 = ax2.barh(etiq, monto.values/1e6, color=colores_r, edgecolor="white", height=0.6)
    for b, v in zip(bs2, monto.values/1e6):
        ax2.text(v+0.5, b.get_y()+b.get_height()/2, f"{v:.1f}M", va="center", fontsize=8)
    ax2.set_xlabel("IVA total cobrado (Gs millones)")
    ax2.set_title("Monto total de IVA por régimen (Gs millones)")
    ax2.grid(axis="x", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A18_iva_efectivo_regimen.png")


# ===========================================================================
# A19 – CARGA TRIBUTARIA EN GUARANÍES POR RÉGIMEN
# Enseña: descomponer la carga total (Derecho, IVA, ISC, Renta, Otros)
# permite ver qué impuesto pesa más según el tipo de operación aduanera.
# Datos: REALES.
# ===========================================================================
def analisis_A19():
    print("\n[A19] Carga tributaria en Gs por régimen")
    tributos = datos.groupby("REGIMEN")[["DERECHO","IVA","ISC","RENTA","OTROS"]].sum()
    tributos  = tributos[tributos.sum(axis=1) > 0]
    tributos.index = [r[:38]+"…" if len(r)>38 else r for r in tributos.index]
    tributos /= 1e6  # convertir a millones de Gs

    fig, ax = plt.subplots(figsize=(13, 6))
    fig.suptitle("Carga Tributaria Total (Gs millones) por Régimen Aduanero (Feb 2026)",
                 fontsize=12, fontweight="bold")

    if tributos.empty:
        ax.text(0.5,0.5,"Sin datos tributarios en este período",
                ha="center",va="center",transform=ax.transAxes,fontsize=12,color="#666")
    else:
        tributos.plot(kind="barh", ax=ax, stacked=True,
                      color=PALETA[:5], edgecolor="white")
        ax.set_xlabel("Monto (Gs millones)")
        ax.legend(title="Tributo", loc="lower right")
        ax.grid(axis="x", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A19_carga_tributaria_gs.png")


# ===========================================================================
# A20 – TOP MARCAS DE ÍTEMS POR FRECUENCIA Y FOB
# Enseña: las marcas más frecuentes en el comercio aduanero revelan qué
# empresas dominan el intercambio. La marca puede cruzarse con el rubro.
# Datos: REALES (columna MARCA ITEM).
# ===========================================================================
def analisis_A20():
    print("\n[A20] Top marcas de ítems")
    d = datos[datos["MARCA ITEM"].notna() &
              ~datos["MARCA ITEM"].isin(["SIN MARCA","NM","S/M","","nan"])].copy()

    if len(d) == 0:
        d = datos.copy()  # usar todos si no hay marcas conocidas

    freq = d["MARCA ITEM"].value_counts().head(10)
    fob  = d.groupby("MARCA ITEM")["FOB DOLAR"].sum().reindex(freq.index)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Top Marcas de Ítems: Frecuencia y FOB Promedio (Feb 2026)",
                 fontsize=12, fontweight="bold")

    colores_m = PALETA[:len(freq)]
    bs = ax1.barh(freq.index, freq.values, color=colores_m, edgecolor="white", height=0.65)
    for b in bs:
        ax1.text(b.get_width()+0.05, b.get_y()+b.get_height()/2,
                 str(int(b.get_width())), va="center", fontsize=9)
    ax1.set_xlabel("Cantidad de ítems")
    ax1.set_title("Marcas más frecuentes en despachos")
    ax1.grid(axis="x", linestyle="--", alpha=0.4)

    bs2 = ax2.barh(freq.index, fob.values/1e3, color=colores_m, edgecolor="white", height=0.65)
    for b, v in zip(bs2, fob.values/1e3):
        ax2.text(v*1.02, b.get_y()+b.get_height()/2, f"${v:.0f}K", va="center", fontsize=8)
    ax2.set_xlabel("FOB total (USD miles)")
    ax2.set_title("FOB total de cada marca")
    ax2.grid(axis="x", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A20_top_marcas.png")


# ===========================================================================
# A21 – RELACIÓN SEGURO vs FLETE POR DESPACHO
# Enseña: el seguro y el flete deberían correlacionarse: rutas más largas
# tienen mayor flete y mayor prima de seguro. La pendiente varía por medio.
# Datos: REALES.
# ===========================================================================
def analisis_A21():
    print("\n[A21] Seguro vs Flete por despacho")
    d = datos[(datos["FLETE DOLAR"] > 0) & (datos["SEGURO DOLAR"] > 0)].copy()

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.suptitle("Relación entre Seguro y Flete por Despacho (Feb 2026)",
                 fontsize=12, fontweight="bold")

    for transp, color in zip(d["MEDIO TRANSPORTE"].unique(), PALETA):
        sub = d[d["MEDIO TRANSPORTE"]==transp]
        ax.scatter(sub["FLETE DOLAR"], sub["SEGURO DOLAR"],
                   label=transp, color=color, s=90, alpha=0.8,
                   edgecolors="white", linewidths=0.8, zorder=4)
        if len(sub) > 1:
            z = np.polyfit(sub["FLETE DOLAR"], sub["SEGURO DOLAR"], 1)
            p = np.poly1d(z)
            xrng = np.linspace(sub["FLETE DOLAR"].min(), sub["FLETE DOLAR"].max(), 50)
            ax.plot(xrng, p(xrng), color=color, linestyle="--", linewidth=1.5, alpha=0.6)

    ax.set_xlabel("Flete (USD)")
    ax.set_ylabel("Seguro (USD)")
    ax.set_title("Cada punto es un despacho; línea = tendencia por medio de transporte")
    ax.legend(title="Medio de transporte")
    ax.grid(linestyle="--", alpha=0.35)

    plt.tight_layout()
    guardar("A21_seguro_vs_flete.png")


# ===========================================================================
# A22 – VALOR IMPONIBLE vs FOB (AJUSTE DE VALOR ADUANERO)
# Enseña: la Aduana puede ajustar el valor declarado (FOB) al valor imponible.
# Diferencias indican gastos de despacho, seguros u otros incluidos/excluidos.
# Datos: REALES.
# ===========================================================================
def analisis_A22():
    print("\n[A22] Valor imponible vs FOB")
    d = datos[(datos["IMPONIBLE DOLAR"] > 0) & (datos["FOB DOLAR"] > 0)].copy()
    d["DIFERENCIA_PCT"] = (d["IMPONIBLE DOLAR"] - d["FOB DOLAR"]) / d["FOB DOLAR"] * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Ajuste de Valor Aduanero: Imponible vs FOB (Feb 2026)",
                 fontsize=12, fontweight="bold")

    for op, color in [("EXPORTACION", VERDE), ("IMPORTACION", ROJO)]:
        sub = d[d["OPERACION"]==op]
        ax1.scatter(sub["FOB DOLAR"]/1e3, sub["IMPONIBLE DOLAR"]/1e3,
                    color=color, label=op, s=80, alpha=0.8,
                    edgecolors="white", linewidths=0.8, zorder=4)
    lim = max(d["IMPONIBLE DOLAR"].max(), d["FOB DOLAR"].max())/1e3 * 1.05
    ax1.plot([0, lim], [0, lim], color="#aaa", linestyle="--",
             linewidth=1.5, label="Imponible = FOB")
    ax1.set_xlabel("FOB (USD miles)")
    ax1.set_ylabel("Valor Imponible (USD miles)")
    ax1.set_title("Imponible vs FOB por despacho\n(sobre la línea = ajuste positivo)")
    ax1.legend()
    ax1.grid(linestyle="--", alpha=0.35)

    colores_d = [VERDE if v >= 0 else ROJO for v in d["DIFERENCIA_PCT"]]
    ax2.bar(range(len(d)), d["DIFERENCIA_PCT"].values,
            color=colores_d, edgecolor="white", width=0.8)
    ax2.axhline(0, color="#555", linewidth=1)
    ax2.set_xlabel("Índice de despacho")
    ax2.set_ylabel("Diferencia (%)\n[(Imponible–FOB)/FOB × 100]")
    ax2.set_title("Ajuste porcentual por despacho")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A22_imponible_vs_fob.png")


# ===========================================================================
# A23 – PRODUCTIVIDAD POR ADUANA
# Enseña: una aduana eficiente procesa más valor (FOB) por despacho en menos
# tiempo. Medir el FOB promedio por despacho es un KPI de productividad.
# Datos: REALES.
# ===========================================================================
def analisis_A23():
    print("\n[A23] Productividad por aduana")
    res = datos.groupby("ADUANA").agg(
        fob_total =("FOB DOLAR","sum"),
        despachos =("DESPACHO CIFRADO","nunique"),
        dias_prom =("DIAS_DESPACHO","mean")
    ).reset_index()
    res["fob_por_despacho"] = res["fob_total"] / res["despachos"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle("Productividad por Aduana: FOB, Despachos y Tiempo Promedio (Feb 2026)",
                 fontsize=12, fontweight="bold")

    metricas = [("fob_por_despacho","FOB Promedio por Despacho (USD)","$"),
                ("despachos","Despachos únicos",""),
                ("dias_prom","Días promedio de despacho","")]

    for ax, (col, titulo, prefijo) in zip(axes, metricas):
        vals = res[col].values
        colores_a = PALETA[:len(res)]
        bs = ax.bar(res["ADUANA"], vals, color=colores_a, edgecolor="white", width=0.6)
        for b, v in zip(bs, vals):
            ax.text(b.get_x()+b.get_width()/2, b.get_height()*1.02,
                    f"{prefijo}{v:,.1f}", ha="center", fontsize=7.5)
        ax.set_title(titulo)
        ax.tick_params(axis="x", rotation=20, labelsize=7.5)
        ax.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A23_productividad_aduana.png")


# ===========================================================================
# A24 – RANKING DE CAPÍTULOS CON NOMBRE COMPLETO
# Enseña: los capítulos arancelarios (2 dígitos) agrupan familias de productos.
# Analizar por nombre permite conectar el código con la mercancía real.
# Datos: REALES.
# ===========================================================================
def analisis_A24():
    print("\n[A24] Ranking capítulos arancelarios nombre completo")
    fob_cap = datos.groupby("CAP_ARANC")["FOB DOLAR"].sum().sort_values(ascending=False).head(8)
    desc    = datos.groupby("CAP_ARANC")["DESC CAPITULO"].first()
    etiq    = [f"Cap {c}: {desc.get(c,'')[:45]}…" if len(desc.get(c,''))>45
               else f"Cap {c}: {desc.get(c,'')}" for c in fob_cap.index]
    pcts    = fob_cap.values / fob_cap.sum() * 100

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Capítulos Arancelarios más Representativos por FOB (Feb 2026)",
                 fontsize=12, fontweight="bold")
    colores = PALETA[:len(fob_cap)]
    barras  = ax.barh(etiq[::-1], fob_cap.values[::-1]/1e3,
                      color=colores[::-1], edgecolor="white", height=0.65)
    for b, pct in zip(barras, pcts[::-1]):
        ax.text(b.get_width()*1.01, b.get_y()+b.get_height()/2,
                f"${b.get_width():.0f}K  ({pct:.1f}%)", va="center", fontsize=8)
    ax.set_xlabel("FOB (USD miles)")
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()
    guardar("A24_capitulos_nombre_completo.png")


# ===========================================================================
# A25 – PRECIO USD/KG: NUEVO vs USADO POR RUBRO
# Enseña: los bienes usados suelen tener menor precio unitario. Comparar
# dentro del mismo rubro permite ver la depreciación implícita.
# Datos: REALES.
# ===========================================================================
def analisis_A25():
    print("\n[A25] Precio USD/kg: Nuevo vs Usado por rubro")
    d = datos[datos["PRECIO_USD_KG"].notna() & (datos["PRECIO_USD_KG"] < 500)].copy()
    pivot = d.groupby(["RUBRO","USO"])["PRECIO_USD_KG"].mean().unstack()
    pivot.index = [r[:35]+"…" if len(r)>35 else r for r in pivot.index]
    pivot = pivot.dropna(how="all")

    if pivot.empty or len(pivot.columns) < 2:
        pivot = d.groupby(["RUBRO","OPERACION"])["PRECIO_USD_KG"].mean().unstack()
        pivot.index = [r[:35]+"…" if len(r)>35 else r for r in pivot.index]

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.suptitle("Precio USD/kg: Comparativa por Condición de Uso y Rubro (Feb 2026)",
                 fontsize=12, fontweight="bold")

    x = np.arange(len(pivot.index))
    ancho = 0.35
    for i, (col, color) in enumerate(zip(pivot.columns, [AZUL, NARANJA, VERDE, ROJO])):
        bs = ax.bar(x + i*ancho, pivot[col].fillna(0), ancho, label=col,
                    color=color, edgecolor="white", alpha=0.85)
        for b in bs:
            if b.get_height() > 0.1:
                ax.text(b.get_x()+b.get_width()/2, b.get_height()*1.02,
                        f"${b.get_height():.1f}", ha="center", fontsize=7.5)
    ax.set_xticks(x + ancho*(len(pivot.columns)-1)/2)
    ax.set_xticklabels(pivot.index, rotation=20, ha="right", fontsize=8)
    ax.set_ylabel("Precio promedio (USD/kg)")
    ax.legend(title="Uso / Operación")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    guardar("A25_precio_nuevo_vs_usado.png")


# ===========================================================================
# A26 – PARTICIPACIÓN DE PAÍSES DE ORIGEN EN IMPORTACIONES
# Enseña: saber de qué países provienen los bienes importados permite evaluar
# la dependencia de ciertos socios y la diversificación del abastecimiento.
# Datos: REALES.
# ===========================================================================
def analisis_A26():
    print("\n[A26] Participación de países de origen en importaciones")
    fob_orig = (imp.groupby("PAIS_ORIGEN_DESC")["FOB DOLAR"]
                .sum().sort_values(ascending=False))
    top_n = 6
    top   = fob_orig.head(top_n)
    resto = fob_orig.iloc[top_n:].sum()
    if resto > 0:
        top = pd.concat([top, pd.Series({"Otros":resto})])

    fob_cnt = imp.groupby("PAIS_ORIGEN_DESC")["FOB DOLAR"].count().sort_values(ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6))
    fig.suptitle("Participación de Países de ORIGEN en Importaciones (Feb 2026)",
                 fontsize=12, fontweight="bold")

    cunas, txts, pcts = ax1.pie(top.values, labels=top.index, autopct="%1.1f%%",
                                 colors=PALETA[:len(top)], startangle=90,
                                 wedgeprops={"edgecolor":"white","linewidth":1.5},
                                 pctdistance=0.75)
    for p in pcts:
        p.set_fontsize(9); p.set_fontweight("bold"); p.set_color("white")
    ax1.set_title(f"Participación por FOB\n(Total: ${fob_orig.sum():,.0f} USD)")

    colores_o = PALETA[:len(fob_cnt)]
    ax2.barh(fob_cnt.index, fob_cnt.values, color=colores_o, edgecolor="white", height=0.6)
    for i, v in enumerate(fob_cnt.values):
        ax2.text(v+0.05, i, str(v), va="center", fontsize=9)
    ax2.set_xlabel("Cantidad de ítems importados")
    ax2.set_title("Frecuencia de ítems por país de origen")
    ax2.grid(axis="x", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A26_paises_origen_importacion.png")


# ===========================================================================
# A27 – COEFICIENTE DE VARIACIÓN DEL PRECIO USD/KG POR RUBRO
# Enseña: el CV = (desviación estándar / media) × 100 mide la dispersión
# relativa. Un CV alto en un rubro indica precios muy irregulares entre ítems.
# Datos: REALES.
# ===========================================================================
def analisis_A27():
    print("\n[A27] Coeficiente de variación del precio USD/kg por rubro")
    d = datos[datos["PRECIO_USD_KG"].notna() & (datos["PRECIO_USD_KG"] < 500)].copy()
    stats = d.groupby("RUBRO")["PRECIO_USD_KG"].agg(
        media="mean", std="std", n="count"
    ).dropna()
    stats["CV"] = stats["std"] / stats["media"] * 100
    stats = stats[stats["n"] >= 1].sort_values("CV", ascending=False)
    etiq  = [r[:35]+"…" if len(r)>35 else r for r in stats.index]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Coeficiente de Variación del Precio USD/kg por Rubro (Feb 2026)",
                 fontsize=12, fontweight="bold")

    colores_cv = [ROJO if v > 50 else NARANJA if v > 25 else VERDE for v in stats["CV"]]
    bs = ax1.barh(etiq, stats["CV"].values, color=colores_cv, edgecolor="white", height=0.65)
    for b, v in zip(bs, stats["CV"].values):
        ax1.text(v+0.5, b.get_y()+b.get_height()/2, f"{v:.1f}%", va="center", fontsize=8)
    ax1.axvline(50, color=ROJO, linestyle="--", linewidth=1, alpha=0.7, label="CV=50% (alta variación)")
    ax1.axvline(25, color=NARANJA, linestyle="--", linewidth=1, alpha=0.7, label="CV=25% (variación media)")
    ax1.set_xlabel("Coeficiente de Variación (%)")
    ax1.set_title("CV por rubro  (mayor CV = precio más irregular)")
    ax1.legend(fontsize=7.5)
    ax1.grid(axis="x", linestyle="--", alpha=0.4)

    ax2.scatter(stats["media"], stats["std"], s=stats["n"]*100,
                color=[PALETA[i%len(PALETA)] for i in range(len(stats))],
                alpha=0.8, edgecolors="white", linewidths=1)
    for i, (rubro, fila) in enumerate(stats.iterrows()):
        ax2.text(fila["media"]+0.5, fila["std"]+0.5, rubro[:20], fontsize=7, color="#333")
    ax2.set_xlabel("Precio promedio USD/kg")
    ax2.set_ylabel("Desviación estándar USD/kg")
    ax2.set_title("Media vs Desviación  (tamaño = n ítems)")
    ax2.grid(linestyle="--", alpha=0.35)

    plt.tight_layout()
    guardar("A27_coeficiente_variacion.png")


# ===========================================================================
# A28 – PERFIL RADAR MULTI-DIMENSIONAL POR ADUANA
# Enseña: el gráfico araña/radar permite comparar múltiples aduanas en 5
# dimensiones simultáneamente (FOB, ítems, días, flete, precio/kg).
# Datos: REALES + normalización min-max.
# ===========================================================================
def analisis_A28():
    print("\n[A28] Perfil radar por aduana")
    res = datos.groupby("ADUANA").agg(
        fob      =("FOB DOLAR","sum"),
        items    =("FOB DOLAR","count"),
        dias     =("DIAS_DESPACHO","mean"),
        flete    =("FLETE DOLAR","mean"),
        precio_kg=("PRECIO_USD_KG","mean")
    ).fillna(0)

    categorias = ["FOB total","Ítems","Días despacho","Flete prom.","USD/kg prom."]
    N = len(categorias)
    angulos = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angulos += angulos[:1]

    # Normalizar 0-1 por columna (invertir días: menos días = mejor)
    norm = res.copy()
    for col in norm.columns:
        rng = norm[col].max() - norm[col].min()
        if rng > 0:
            if col == "dias":
                norm[col] = 1 - (norm[col] - norm[col].min()) / rng
            else:
                norm[col] = (norm[col] - norm[col].min()) / rng
        else:
            norm[col] = 0.5

    fig, ax = plt.subplots(figsize=(8, 7), subplot_kw={"polar": True})
    fig.suptitle("Perfil Radar por Aduana – 5 Dimensiones Normalizadas (Feb 2026)",
                 fontsize=12, fontweight="bold")

    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25","0.5","0.75","1.0"], fontsize=7)

    for (aduana, fila), color in zip(norm.iterrows(), PALETA):
        vals = fila.tolist() + fila.tolist()[:1]
        ax.plot(angulos, vals, color=color, linewidth=2, label=aduana)
        ax.fill(angulos, vals, color=color, alpha=0.08)

    ax.legend(loc="lower right", bbox_to_anchor=(1.4, -0.1), fontsize=8)
    plt.tight_layout()
    guardar("A28_radar_aduanas.png")


# ===========================================================================
# A29 – DISTRIBUCIÓN DE ÍTEMS POR DESPACHO
# Enseña: un despacho puede tener uno o varios ítems (posiciones). Conocer
# la distribución ayuda a entender la complejidad operativa de cada despacho.
# Datos: REALES.
# ===========================================================================
def analisis_A29():
    print("\n[A29] Distribución de ítems por despacho")
    items_por_despacho = (datos.groupby("DESPACHO CIFRADO")["ITEM"]
                          .nunique().reset_index(name="n_items"))
    vals = items_por_despacho["n_items"].values
    sorted_vals = np.sort(vals)
    cdf = np.arange(1, len(sorted_vals)+1) / len(sorted_vals)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Distribución de Ítems por Despacho (Feb 2026)",
                 fontsize=12, fontweight="bold")

    n_vals = int(vals.max()) + 1
    counts = [(vals == i).sum() for i in range(1, n_vals)]
    ax1.bar(range(1, n_vals), counts, color=AZUL, edgecolor="white", alpha=0.85, width=0.7)
    for x, cnt in zip(range(1, n_vals), counts):
        if cnt > 0:
            ax1.text(x, cnt+0.05, str(cnt), ha="center", fontsize=9)
    ax1.axvline(vals.mean(), color=NARANJA, linestyle="--", linewidth=2,
                label=f"Promedio: {vals.mean():.2f} ítems")
    ax1.set_xlabel("Cantidad de ítems por despacho")
    ax1.set_ylabel("Frecuencia (despachos)")
    ax1.set_title("Histograma de ítems por despacho")
    ax1.legend()
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    ax2.plot(sorted_vals, cdf, color=AZUL, linewidth=2.5)
    ax2.fill_between(sorted_vals, cdf, alpha=0.12, color=AZUL)
    ax2.axhline(0.5, color="#aaa", linestyle="--", linewidth=1, alpha=0.7)
    ax2.text(sorted_vals[-1]*0.02, 0.52, "50% de despachos", fontsize=7.5, color="#aaa")
    ax2.set_xlabel("Cantidad de ítems por despacho")
    ax2.set_ylabel("Probabilidad acumulada (CDF)")
    ax2.set_title("Función de distribución acumulada")
    ax2.grid(linestyle="--", alpha=0.35)

    plt.tight_layout()
    guardar("A29_items_por_despacho.png")


# ===========================================================================
# A30 – TASA TRIBUTARIA EFECTIVA POR RÉGIMEN
# Enseña: la tasa efectiva = (Tributos totales / Imponible Gs) × 100.
# Compara cuánto tributa cada régimen respecto a su base imponible.
# Datos: REALES.
# ===========================================================================
def analisis_A30():
    print("\n[A30] Tasa tributaria efectiva por régimen")
    d = datos[datos["IMPONIBLE GS"] > 0].copy()
    tasa = d.groupby("REGIMEN")["TASA_TRIB_PCT"].mean().sort_values(ascending=False)
    monto_base = d.groupby("REGIMEN")["IMPONIBLE GS"].sum().reindex(tasa.index) / 1e6
    etiq = [r[:40]+"…" if len(r)>40 else r for r in tasa.index]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Tasa Tributaria Efectiva (%) por Régimen Aduanero (Feb 2026)",
                 fontsize=12, fontweight="bold")

    colores_r = [ROJO if v > 15 else NARANJA if v > 5 else VERDE for v in tasa.values]
    bs = ax1.barh(etiq, tasa.values, color=colores_r, edgecolor="white", height=0.65)
    for b, v in zip(bs, tasa.values):
        ax1.text(v+0.1, b.get_y()+b.get_height()/2, f"{v:.2f}%", va="center", fontsize=8)
    ax1.axvline(10, color=NARANJA, linestyle="--", linewidth=1, alpha=0.7,
                label="10% referencia")
    ax1.set_xlabel("Tasa tributaria efectiva (%)")
    ax1.set_title("Tributos / Imponible Gs × 100")
    ax1.legend()
    ax1.grid(axis="x", linestyle="--", alpha=0.4)

    colores_r2 = PALETA[:len(monto_base)]
    bs2 = ax2.barh(etiq, monto_base.values, color=colores_r2, edgecolor="white", height=0.65)
    for b, v in zip(bs2, monto_base.values):
        ax2.text(v*1.01, b.get_y()+b.get_height()/2, f"Gs {v:.0f}M", va="center", fontsize=8)
    ax2.set_xlabel("Base imponible (Gs millones)")
    ax2.set_title("Base imponible total por régimen")
    ax2.grid(axis="x", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A30_tasa_tributaria_efectiva.png")


# ===========================================================================
# A31 – KILO BRUTO vs KILO NETO: ANÁLISIS DE DIFERENCIA
# Enseña: la distancia respecto a la línea y=x indica el peso del embalaje.
# Puntos muy alejados pueden indicar errores de declaración.
# Datos: REALES.
# ===========================================================================
def analisis_A31():
    print("\n[A31] Kilo Bruto vs Kilo Neto")
    d = datos[(datos["KILO NETO"] > 0) & (datos["KILO BRUTO"] > 0)].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Kilo Bruto vs Kilo Neto: Peso del Embalaje (Feb 2026)",
                 fontsize=12, fontweight="bold")

    for op, color in [("EXPORTACION", VERDE), ("IMPORTACION", ROJO)]:
        sub = d[d["OPERACION"]==op]
        ax1.scatter(sub["KILO NETO"]/1e3, sub["KILO BRUTO"]/1e3,
                    color=color, label=op, s=80, alpha=0.8,
                    edgecolors="white", linewidths=0.8, zorder=4)
    lim = max(d["KILO BRUTO"].max(), d["KILO NETO"].max())/1e3 * 1.05
    ax1.plot([0,lim],[0,lim], color="#aaa", linestyle="--", linewidth=1.5, label="Bruto=Neto")
    ax1.set_xlabel("Kilo Neto (miles kg)")
    ax1.set_ylabel("Kilo Bruto (miles kg)")
    ax1.set_title("Scatter: sobre la línea = hay embalaje")
    ax1.legend()
    ax1.grid(linestyle="--", alpha=0.35)

    d["DIFERENCIA_KG"] = d["KILO BRUTO"] - d["KILO NETO"]
    colores_d = [VERDE if op == "EXPORTACION" else ROJO for op in d["OPERACION"]]
    ax2.bar(range(len(d)), d["DIFERENCIA_KG"].values,
            color=colores_d, edgecolor="white", width=0.8, alpha=0.85)
    ax2.axhline(d["DIFERENCIA_KG"].mean(), color=NARANJA, linestyle="--",
                linewidth=2, label=f"Prom: {d['DIFERENCIA_KG'].mean():.1f} kg")
    ax2.set_xlabel("Índice de despacho")
    ax2.set_ylabel("Diferencia (Bruto − Neto) en kg")
    ax2.set_title("Peso del embalaje por despacho")
    ax2.legend()
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    leyenda_col = [mpatches.Patch(color=VERDE, label="Exportación"),
                   mpatches.Patch(color=ROJO,  label="Importación")]
    ax2.legend(handles=ax2.get_legend_handles_labels()[0]+leyenda_col,
               labels=ax2.get_legend_handles_labels()[1]+["Exportación","Importación"])

    plt.tight_layout()
    guardar("A31_kilo_bruto_vs_neto.png")


# ===========================================================================
# A32 – FOB POR ACUERDO COMERCIAL Y OPERACIÓN
# Enseña: desagregar el FOB por acuerdo y operación muestra si los acuerdos
# benefician más a exportadores o importadores.
# Datos: REALES.
# ===========================================================================
def analisis_A32():
    print("\n[A32] FOB por acuerdo y operación")
    tabla = (datos.groupby(["ACUERDO","OPERACION"])["FOB DOLAR"]
             .sum().unstack(fill_value=0))
    cnt   = (datos.groupby(["ACUERDO","OPERACION"]).size().unstack(fill_value=0))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 9))
    fig.suptitle("Acuerdos Comerciales: FOB y Cantidad de Despachos por Operación (Feb 2026)",
                 fontsize=12, fontweight="bold")

    x = np.arange(len(tabla.index))
    ancho = 0.35
    for i, (col, color) in enumerate(zip(tabla.columns, [VERDE, ROJO])):
        bs = ax1.bar(x + i*ancho, tabla[col]/1e3, ancho, label=col,
                     color=color, edgecolor="white", alpha=0.85)
        for b in bs:
            if b.get_height() > 0:
                ax1.text(b.get_x()+b.get_width()/2, b.get_height()*1.02,
                         f"${b.get_height():.0f}K", ha="center", fontsize=8)
    ax1.set_xticks(x + ancho/2)
    ax1.set_xticklabels(tabla.index, rotation=15, ha="right")
    ax1.set_ylabel("FOB (USD miles)")
    ax1.set_title("Valor FOB por acuerdo y tipo de operación")
    ax1.legend(title="Operación")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for i, (col, color) in enumerate(zip(cnt.columns, [VERDE, ROJO])):
        bs = ax2.bar(x + i*ancho, cnt[col], ancho, label=col,
                     color=color, edgecolor="white", alpha=0.85)
        for b in bs:
            if b.get_height() > 0:
                ax2.text(b.get_x()+b.get_width()/2, b.get_height()*1.05,
                         str(int(b.get_height())), ha="center", fontsize=9)
    ax2.set_xticks(x + ancho/2)
    ax2.set_xticklabels(cnt.index, rotation=15, ha="right")
    ax2.set_ylabel("Cantidad de despachos")
    ax2.set_title("Cantidad de despachos por acuerdo")
    ax2.legend(title="Operación")
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A32_fob_acuerdo_operacion.png")


# ===========================================================================
# A33 – CONCENTRACIÓN DE FOB POR ADUANA (HHI SECTORIAL)
# Enseña: aplicar el HHI dentro de cada operación por aduana muestra si
# una sola aduana domina las exportaciones o si hay distribución equilibrada.
# Datos: REALES.
# ===========================================================================
def analisis_A33():
    print("\n[A33] Concentración HHI por aduana y operación")
    def hhi(serie):
        if serie.sum() == 0: return 0
        partic = serie / serie.sum() * 100
        return (partic**2).sum()

    resultados = []
    for op in datos["OPERACION"].unique():
        sub  = datos[datos["OPERACION"]==op]
        fob  = sub.groupby("ADUANA")["FOB DOLAR"].sum()
        val  = hhi(fob)
        cnt  = len(fob)
        resultados.append({"OPERACION":op, "HHI":val, "n_aduanas":cnt})
    res = pd.DataFrame(resultados)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Índice de Concentración HHI de Aduanas por Tipo de Operación (Feb 2026)",
                 fontsize=12, fontweight="bold")

    colores_op = [VERDE if op=="EXPORTACION" else ROJO for op in res["OPERACION"]]
    bs = ax1.bar(res["OPERACION"], res["HHI"], color=colores_op, edgecolor="white", width=0.5)
    for b, v in zip(bs, res["HHI"]):
        ax1.text(b.get_x()+b.get_width()/2, v+50, f"HHI={v:.0f}", ha="center", fontsize=10)
    ax1.axhline(2500, color=ROJO, linestyle="--", linewidth=1.2, alpha=0.7)
    ax1.axhline(1500, color=NARANJA, linestyle="--", linewidth=1.2, alpha=0.7)
    ax1.text(1.4, 2520, "Concentrado (>2500)", fontsize=7.5, color=ROJO)
    ax1.text(1.4, 1520, "Moderado (>1500)", fontsize=7.5, color=NARANJA)
    ax1.set_ylabel("HHI")
    ax1.set_title("HHI de concentración de aduanas")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for op, color in [("EXPORTACION", VERDE), ("IMPORTACION", ROJO)]:
        sub = datos[datos["OPERACION"]==op]
        fob_aduana = sub.groupby("ADUANA")["FOB DOLAR"].sum().sort_values(ascending=True)
        ax2.barh(fob_aduana.index, fob_aduana.values/1e3, color=color,
                 edgecolor="white", alpha=0.7, height=0.3,
                 label=op,
                 left=0 if op=="EXPORTACION" else fob_aduana.values.max()/1e3 * 0)
    ax2.set_xlabel("FOB (USD miles)")
    ax2.set_title("FOB por aduana y operación")
    ax2.legend()
    ax2.grid(axis="x", linestyle="--", alpha=0.4)

    plt.tight_layout()
    guardar("A33_hhi_aduanas.png")


# ===========================================================================
# A34 – MAPA DE CALOR ACUERDO × PAÍS DESTINO
# Enseña: ver si los acuerdos comerciales se usan efectivamente con los países
# para los que fueron diseñados (MERCOSUR → Brasil, Argentina, etc.).
# Datos: REALES.
# ===========================================================================
def analisis_A34():
    print("\n[A34] Heatmap Acuerdo × País Destino")
    pivot = (datos.groupby(["ACUERDO","PAIS_DEST_DESC"])["FOB DOLAR"]
             .sum().unstack(fill_value=0))
    pivot.columns = [p[:12]+"…" if len(p)>12 else p for p in pivot.columns]

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.suptitle("FOB por Acuerdo Comercial y País Destino (Feb 2026)",
                 fontsize=12, fontweight="bold")
    sns.heatmap(pivot/1e3, ax=ax, annot=True, fmt=".0f", cmap="PuBu",
                linewidths=0.5, cbar_kws={"label":"FOB (USD miles)"})
    ax.set_xlabel("País de Destino")
    ax.set_ylabel("Acuerdo Comercial")
    ax.set_title("Cada celda: FOB total en USD miles (0 = sin operaciones)", fontsize=8)
    plt.tight_layout()
    guardar("A34_heatmap_acuerdo_pais.png")


# ===========================================================================
# A35 – ANÁLISIS DE AJUSTES ADUANEROS
# Enseña: los ajustes (positivos o negativos) modifican el valor FOB declarado.
# Un ajuste positivo aumenta el valor imponible; uno negativo lo reduce.
# Datos: REALES (columnas AJUSTE A INCLUIR / AJUSTE A DEDUCIR).
# ===========================================================================
def analisis_A35():
    print("\n[A35] Ajustes aduaneros")
    d = datos.copy()
    d["AJUSTE_NETO"] = d["AJUSTE A INCLUIR"] - d["AJUSTE A DEDUCIR"]
    con_ajuste = d[d["AJUSTE_NETO"] != 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Ajustes de Valor Aduanero: Incluir vs Deducir (Feb 2026)",
                 fontsize=12, fontweight="bold")

    categorias_aj = ["Con ajuste positivo","Sin ajuste","Con ajuste negativo"]
    conteos = [
        (d["AJUSTE_NETO"] > 0).sum(),
        (d["AJUSTE_NETO"] == 0).sum(),
        (d["AJUSTE_NETO"] < 0).sum()
    ]
    colores_aj = [VERDE, "#AAAAAA", ROJO]
    bs = ax1.bar(categorias_aj, conteos, color=colores_aj, edgecolor="white", width=0.6)
    for b, v in zip(bs, conteos):
        ax1.text(b.get_x()+b.get_width()/2, v+0.1, str(v), ha="center", fontsize=11)
    ax1.set_ylabel("Cantidad de despachos")
    ax1.set_title("Distribución de ajustes de valor")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    if len(con_ajuste) > 0:
        colores_ind = [VERDE if v > 0 else ROJO for v in con_ajuste["AJUSTE_NETO"]]
        ax2.bar(range(len(con_ajuste)), con_ajuste["AJUSTE_NETO"].values,
                color=colores_ind, edgecolor="white", width=0.8)
        ax2.axhline(0, color="#555", linewidth=1)
        for i, (_, fila) in enumerate(con_ajuste.iterrows()):
            ax2.text(i, fila["AJUSTE_NETO"] + (50 if fila["AJUSTE_NETO"]>0 else -200),
                     f"${fila['AJUSTE_NETO']:,.0f}", ha="center", fontsize=7.5)
        ax2.set_xlabel("Índice de despacho con ajuste")
        ax2.set_ylabel("Ajuste neto (USD)")
        ax2.set_title("Magnitud del ajuste por despacho\n(Positivo = sube el imponible)")
    else:
        ax2.text(0.5, 0.5, "No hay despachos con ajuste\nen este período",
                 ha="center", va="center", transform=ax2.transAxes, fontsize=12, color="#666")

    # Complementar con simulación didáctica si no hay ajustes reales
    if len(con_ajuste) == 0:
        ajustes_sim = np.random.normal(0, 5000, 10)
        colores_sim = [VERDE if v>0 else ROJO for v in ajustes_sim]
        ax2.bar(range(10), ajustes_sim, color=colores_sim, edgecolor="white", width=0.8)
        ax2.axhline(0, color="#555", linewidth=1)
        ax2.set_xlabel("Despacho (simulado)")
        ax2.set_ylabel("Ajuste neto (USD)")
        ax2.set_title("Ejemplo de ajuste por despacho\n[Datos simulados]")
        ax2.annotate("⚠ Datos simulados pedagógicos",
                     xy=(0.01,-0.12), xycoords="axes fraction",
                     fontsize=7, color="#888", style="italic")

    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    guardar("A35_ajustes_aduaneros.png")


# ===========================================================================
# A36 – PERFIL ARAÑA EXPORTACIÓN vs IMPORTACIÓN
# Enseña: el radar con métricas normalizadas permite ver en una sola imagen
# si Paraguay exporta mercancías más voluminosas, caras, rápidas, etc.
# Datos: REALES + normalización min-max.
# ===========================================================================
def analisis_A36():
    print("\n[A36] Perfil araña exportación vs importación")
    metricas_radar = {
        "FOB total (USD)":     [exp["FOB DOLAR"].sum(), imp["FOB DOLAR"].sum()],
        "Peso neto (kg)":      [exp["KILO NETO"].sum(), imp["KILO NETO"].sum()],
        "Precio USD/kg":       [exp["PRECIO_USD_KG"].mean(), imp["PRECIO_USD_KG"].mean()],
        "Días despacho":       [exp["DIAS_DESPACHO"].mean(), imp["DIAS_DESPACHO"].mean()],
        "Flete/FOB (%)":       [(exp["FLETE DOLAR"].sum()/exp["FOB DOLAR"].sum()*100),
                                (imp["FLETE DOLAR"].sum()/imp["FOB DOLAR"].sum()*100)],
        "Seguro/CIF (%)":      [exp["SEGURO_PCT_CIF"].mean(), imp["SEGURO_PCT_CIF"].mean()],
    }
    etiq_radar = list(metricas_radar.keys())
    N = len(etiq_radar)
    angulos = np.linspace(0, 2*np.pi, N, endpoint=False).tolist()
    angulos += angulos[:1]

    vals_raw = np.array([v for v in metricas_radar.values()])
    max_vals = vals_raw.max(axis=1)
    max_vals[max_vals == 0] = 1
    vals_norm = (vals_raw / max_vals[:, None])

    exp_vals = vals_norm[:,0].tolist() + vals_norm[:,0].tolist()[:1]
    imp_vals = vals_norm[:,1].tolist() + vals_norm[:,1].tolist()[:1]

    fig, ax = plt.subplots(figsize=(8, 7), subplot_kw={"polar":True})
    fig.suptitle("Perfil Comparativo: Exportación vs Importación (Feb 2026)\n"
                 "(Métricas normalizadas 0–1 respecto al máximo de cada dimensión)",
                 fontsize=11, fontweight="bold")

    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(etiq_radar, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["25%","50%","75%","100%"], fontsize=7)

    ax.plot(angulos, exp_vals, color=VERDE, linewidth=2.5, label="Exportación")
    ax.fill(angulos, exp_vals, color=VERDE, alpha=0.15)
    ax.plot(angulos, imp_vals, color=ROJO, linewidth=2.5, label="Importación")
    ax.fill(angulos, imp_vals, color=ROJO, alpha=0.15)

    ax.legend(loc="lower right", bbox_to_anchor=(1.35, -0.1))

    # Añadir valores reales como anotación
    nota = "\n".join([f"{k}: Exp={v[0]:.2f} | Imp={v[1]:.2f}"
                      for k, v in metricas_radar.items()])
    fig.text(0.02, 0.01, nota, fontsize=6.5, color="#555", va="bottom",
             family="monospace")

    plt.tight_layout()
    guardar("A36_radar_exp_vs_imp.png")


# ===========================================================================
# A37 – DASHBOARD INTEGRADO DWH: 4 ANÁLISIS CRUZADOS
# Enseña: un dashboard de 4 paneles integra dimensiones del DWH para dar
# una visión ejecutiva completa del comercio exterior en un solo vistazo.
# Combina: aduana, régimen, transporte y valor para toma de decisiones.
# Datos: REALES.
# ===========================================================================
def analisis_A37():
    print("\n[A37] Dashboard integrado DWH")
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("DASHBOARD EJECUTIVO – Comercio Exterior Paraguay (Feb 2026)\n"
                 "Data Warehouse · 4 Análisis Integrados",
                 fontsize=14, fontweight="bold")

    # ── Panel 1 (superior izquierdo): FOB por operación y aduana ──────────
    ax1 = fig.add_subplot(2, 2, 1)
    pivot1 = datos.groupby(["ADUANA","OPERACION"])["FOB DOLAR"].sum().unstack(fill_value=0)/1e3
    x = np.arange(len(pivot1.index))
    ancho = 0.35
    for i, (col, color) in enumerate(zip(pivot1.columns, [VERDE, ROJO])):
        bs = ax1.bar(x+i*ancho, pivot1[col], ancho, label=col, color=color,
                     edgecolor="white", alpha=0.85)
    ax1.set_xticks(x+ancho/2)
    ax1.set_xticklabels(pivot1.index, rotation=20, fontsize=7.5)
    ax1.set_ylabel("FOB (USD miles)")
    ax1.set_title("① FOB por Aduana y Operación")
    ax1.legend(fontsize=8)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    # ── Panel 2 (superior derecho): distribución por transporte ──────────
    ax2 = fig.add_subplot(2, 2, 2)
    pivot2 = datos.groupby(["MEDIO TRANSPORTE","OPERACION"])["FOB DOLAR"].sum().unstack(fill_value=0)/1e3
    pivot2.plot(kind="bar", ax=ax2, color=[VERDE, ROJO], edgecolor="white", alpha=0.85)
    ax2.set_xticklabels(pivot2.index, rotation=15, fontsize=9)
    ax2.set_ylabel("FOB (USD miles)")
    ax2.set_title("② FOB por Medio de Transporte")
    ax2.legend(fontsize=8)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # ── Panel 3 (inferior izquierdo): tiempo despacho por régimen ────────
    ax3 = fig.add_subplot(2, 2, 3)
    tiempos_reg = (datos.groupby("REGIMEN")["DIAS_DESPACHO"]
                   .mean().sort_values(ascending=False).dropna())
    etiq3 = [r[:30]+"…" if len(r)>30 else r for r in tiempos_reg.index]
    colores3 = [ROJO if v > 5 else NARANJA if v > 2 else VERDE for v in tiempos_reg.values]
    bs3 = ax3.barh(etiq3, tiempos_reg.values, color=colores3, edgecolor="white", height=0.6)
    for b, v in zip(bs3, tiempos_reg.values):
        ax3.text(v+0.05, b.get_y()+b.get_height()/2, f"{v:.1f}d", va="center", fontsize=8)
    ax3.set_xlabel("Días promedio")
    ax3.set_title("③ Tiempo Despacho por Régimen")
    ax3.grid(axis="x", linestyle="--", alpha=0.4)

    # ── Panel 4 (inferior derecho): scatter precio/kg vs flete ──────────
    ax4 = fig.add_subplot(2, 2, 4)
    d4 = datos[datos["PRECIO_USD_KG"].notna() & (datos["PRECIO_USD_KG"]<500) &
               (datos["FLETE DOLAR"]>0)].copy()
    for op, color in [("EXPORTACION", VERDE), ("IMPORTACION", ROJO)]:
        sub = d4[d4["OPERACION"]==op]
        ax4.scatter(sub["FLETE DOLAR"], sub["PRECIO_USD_KG"],
                    color=color, label=op, s=70, alpha=0.8,
                    edgecolors="white", linewidths=0.7, zorder=4)
    ax4.set_xlabel("Flete (USD)")
    ax4.set_ylabel("Precio unitario (USD/kg)")
    ax4.set_title("④ Flete vs Precio USD/kg")
    ax4.legend(fontsize=8)
    ax4.grid(linestyle="--", alpha=0.35)
    ax4.spines["top"].set_visible(False)
    ax4.spines["right"].set_visible(False)

    # ── KPIs en el pie de página ─────────────────────────────────────────
    kpis = (f"KPIs Feb 2026 ▸  "
            f"FOB total: ${datos['FOB DOLAR'].sum():,.0f} USD  |  "
            f"Despachos: {datos['DESPACHO CIFRADO'].nunique()}  |  "
            f"Aduanas: {datos['ADUANA'].nunique()}  |  "
            f"Países destino: {datos['PAIS_DEST_DESC'].nunique()}  |  "
            f"Tiempo prom: {datos['DIAS_DESPACHO'].mean():.1f} días")
    fig.text(0.5, 0.01, kpis, ha="center", fontsize=9, color="#333",
             bbox=dict(boxstyle="round", facecolor="#F0F4F8", alpha=0.8))

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    guardar("A37_dashboard_integrado.png")


# ==============================================================================
# MAPA DE FUNCIONES
# ==============================================================================
ANALISIS = {
    "A01": analisis_A01, "A02": analisis_A02, "A03": analisis_A03,
    "A04": analisis_A04, "A05": analisis_A05, "A06": analisis_A06,
    "A07": analisis_A07, "A08": analisis_A08, "A09": analisis_A09,
    "A10": analisis_A10, "A11": analisis_A11, "A12": analisis_A12,
    "A13": analisis_A13, "A14": analisis_A14, "A15": analisis_A15,
    "A16": analisis_A16, "A17": analisis_A17, "A18": analisis_A18,
    "A19": analisis_A19, "A20": analisis_A20, "A21": analisis_A21,
    "A22": analisis_A22, "A23": analisis_A23, "A24": analisis_A24,
    "A25": analisis_A25, "A26": analisis_A26, "A27": analisis_A27,
    "A28": analisis_A28, "A29": analisis_A29, "A30": analisis_A30,
    "A31": analisis_A31, "A32": analisis_A32, "A33": analisis_A33,
    "A34": analisis_A34, "A35": analisis_A35, "A36": analisis_A36,
    "A37": analisis_A37,
}


# ==============================================================================
# EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cod = sys.argv[1].upper()
        if cod in ANALISIS:
            print(f"\n{'='*60}")
            print(f"  Alumno {cod}: {CATALOGO[cod]}")
            print(f"{'='*60}")
            ANALISIS[cod]()
        else:
            print(f"Código '{cod}' no existe. Opciones: {list(ANALISIS.keys())}")
    else:
        print("\n" + "="*65)
        print("  GENERANDO LOS 37 ANÁLISIS – TODOS LOS ALUMNOS")
        print("="*65)
        for cod, fn in ANALISIS.items():
            print(f"\n{'─'*50}")
            print(f"  {cod} – {CATALOGO[cod]}")
            print(f"{'─'*50}")
            fn()

    print("\n" + "="*65)
    generados = sorted(SALIDA.glob("*.png"))
    print(f"  COMPLETADO – {len(generados)} gráficos en: {SALIDA}")
    print("="*65)
    print("\nASIGNACIÓN POR ALUMNO:")
    for cod, desc in CATALOGO.items():
        print(f"  {cod}  →  {desc}")
