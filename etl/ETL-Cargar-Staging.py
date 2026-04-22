import duckdb
import pandas as pd
import os
import re

DB_PATH   = r"C:\Información\proyectos\aduana_bi\db\aduana.duckdb"
XLSX_PATH = r"C:\Información\proyectos\aduana_bi\data_lake\bronze\DatosXLSX.xlsx"
DEST_PATH = r"C:\Información\proyectos\aduana_bi\data_lake\bronze\LISTADO_DE_DESTINACIONES.xlsx"

con = duckdb.connect(DB_PATH)

try:
    con.execute("DELETE FROM dw.stg_aduana;")
    con.execute("DELETE FROM dw.stg_destinaciones;")
except:
    print("Tablas no existen aún, se omite DELETE.")

# ----------------------------------------------------------
# Leer desde Excel directamente (evita el problema del ; en CSV)
# y convertir fechas con pandas antes de pasar a DuckDB
# ----------------------------------------------------------
df = pd.read_excel(XLSX_PATH)

# Convertir fechas: el Excel las tiene como texto 'DD/MM/YYYY'
df['OFICIALIZACION'] = pd.to_datetime(df['OFICIALIZACION'], format='%d/%m/%Y', errors='coerce').dt.date
df['CANCELACION']    = pd.to_datetime(df['CANCELACION'],    format='%d/%m/%Y', errors='coerce').dt.date

# Verificar antes de insertar
nulls_ofic = df['OFICIALIZACION'].isna().sum()
nulls_canc = df['CANCELACION'].isna().sum()
print(f"Filas leídas del Excel: {len(df)}")
print(f"Fechas OFICIALIZACION NULL: {nulls_ofic}")
print(f"Fechas CANCELACION NULL:    {nulls_canc}")

if nulls_ofic == len(df):
    raise ValueError("ERROR CRÍTICO: 100% de OFICIALIZACION son NULL. Verificar formato.")

# Renombrar columnas al nombre esperado por la tabla staging
df = df.rename(columns={
    'DESPACHO CIFRADO'          : 'despacho_cifrado',
    'OPERACION'                 : 'operacion',
    'DESTINACION'               : 'destinacion',
    'REGIMEN'                   : 'regimen',
    'OFICIALIZACION'            : 'oficializacion',
    'CANCELACION'               : 'cancelacion',
    'AÑO'                       : 'anio',
    'MES'                       : 'mes',
    'ADUANA'                    : 'aduana',
    'COTIZACION'                : 'cotizacion',
    'MEDIO TRANSPORTE'          : 'medio_transporte',
    'CANAL'                     : 'canal',
    'ITEM'                      : 'item',
    'PAIS ORIGEN'               : 'pais_origen',
    'PAIS PROCEDENCIA/DESTINO'  : 'pais_procedencia_destino',
    'USO'                       : 'uso',
    'UNIDAD MEDIDA ESTADISTICA' : 'unidad_medida_estadistica',
    'CANTIDAD ESTADISTICA'      : 'cantidad_estadistica',
    'KILO NETO'                 : 'kilo_neto',
    'KILO BRUTO'                : 'kilo_bruto',
    'FOB DOLAR'                 : 'fob_dolar',
    'FLETE DOLAR'               : 'flete_dolar',
    'SEGURO DOLAR'              : 'seguro_dolar',
    'IMPONIBLE DOLAR'           : 'imponible_dolar',
    'IMPONIBLE GS'              : 'imponible_gs',
    'AJUSTE A INCLUIR'          : 'ajuste_a_incluir',
    'AJUSTE A DEDUCIR'          : 'ajuste_a_deducir',
    'POSICION'                  : 'posicion',
    'RUBRO'                     : 'rubro',
    'DESC CAPITULO'             : 'desc_capitulo',
    'DESC POSICION'             : 'desc_posicion',
    'DESC PARTIDA'              : 'desc_partida',
    'MERCADERIA'                : 'mercaderia',
    'MARCA ITEM'                : 'marca_item',
    'ACUERDO'                   : 'acuerdo',
    'DERECHO'                   : 'derecho',
    'ISC'                       : 'isc',
    'SERVICIO'                  : 'servicio',
    'RENTA'                     : 'renta',
    'IVA'                       : 'iva',
    'OTROS'                     : 'otros',
    'TOTAL'                     : 'total',
})

# Registrar el DataFrame y volcar en staging con los tipos correctos
con.register('df_stg', df)
con.execute("""
INSERT INTO dw.stg_aduana
SELECT
    CAST(despacho_cifrado           AS VARCHAR),
    CAST(operacion                  AS VARCHAR),
    CAST(destinacion                AS VARCHAR),
    CAST(regimen                    AS VARCHAR),
    CAST(oficializacion             AS DATE),
    CAST(cancelacion                AS DATE),
    CAST(anio                       AS INTEGER),
    CAST(mes                        AS VARCHAR),
    CAST(aduana                     AS VARCHAR),
    CAST(cotizacion                 AS DOUBLE),
    CAST(medio_transporte           AS VARCHAR),
    CAST(canal                      AS VARCHAR),
    CAST(item                       AS INTEGER),
    CAST(pais_origen                AS VARCHAR),
    CAST(pais_procedencia_destino   AS VARCHAR),
    CAST(uso                        AS VARCHAR),
    CAST(unidad_medida_estadistica  AS VARCHAR),
    CAST(cantidad_estadistica       AS DOUBLE),
    CAST(kilo_neto                  AS DOUBLE),
    CAST(kilo_bruto                 AS DOUBLE),
    CAST(fob_dolar                  AS DOUBLE),
    CAST(flete_dolar                AS DOUBLE),
    CAST(seguro_dolar               AS DOUBLE),
    CAST(imponible_dolar            AS DOUBLE),
    CAST(imponible_gs               AS DOUBLE),
    CAST(ajuste_a_incluir           AS DOUBLE),
    CAST(ajuste_a_deducir           AS DOUBLE),
    CAST(posicion                   AS VARCHAR),
    CAST(rubro                      AS VARCHAR),
    CAST(desc_capitulo              AS VARCHAR),
    CAST(desc_posicion              AS VARCHAR),
    CAST(desc_partida               AS VARCHAR),
    CAST(mercaderia                 AS VARCHAR),
    CAST(marca_item                 AS VARCHAR),
    CAST(acuerdo                    AS VARCHAR),
    CAST(derecho                    AS DOUBLE),
    CAST(isc                        AS DOUBLE),
    CAST(servicio                   AS DOUBLE),
    CAST(renta                      AS DOUBLE),
    CAST(iva                        AS DOUBLE),
    CAST(otros                      AS DOUBLE),
    CAST(total                      AS DOUBLE)
FROM df_stg;
""")

filas = con.execute("SELECT COUNT(*) FROM dw.stg_aduana").fetchone()[0]
print(f"stg_aduana cargada: {filas} filas")

# ----------------------------------------------------------
# Carga del catálogo de destinaciones (sin cambios)
# ----------------------------------------------------------
if os.path.exists(DEST_PATH):
    try:
        df_dest = pd.read_excel(DEST_PATH)
        df_dest.columns = [
            re.sub(r'^[^A-Z0-9]+', '', c.strip().upper())
            for c in df_dest.columns
        ]
        df_dest = df_dest.rename(columns={
            "CÓD."                              : "cod_destinacion",
            "COD."                              : "cod_destinacion",
            "DESCRIPCIÓN"                       : "descripcion_dest",
            "DESCRIPCION"                       : "descripcion_dest",
            "SUSPENSIVO - DEFINITIVO - TEMPORAL": "tipo_regimen_base",
            "IMPORT / EXPORT"                   : "tipo_operacion_base"
        })
        if "tipo_regimen_base"   not in df_dest.columns: df_dest["tipo_regimen_base"]   = None
        if "tipo_operacion_base" not in df_dest.columns: df_dest["tipo_operacion_base"] = None
        df_dest = df_dest[["cod_destinacion","descripcion_dest","tipo_regimen_base","tipo_operacion_base"]]
        con.register("df_dest", df_dest)
        con.execute("INSERT INTO dw.stg_destinaciones SELECT * FROM df_dest;")
        print("stg_destinaciones cargada correctamente.")
    except Exception as e:
        print(f"Error cargando Excel de destinaciones: {e}")
else:
    print("Aviso: no se encontró LISTADO_DE_DESTINACIONES.xlsx. Se continúa sin catálogo.")

con.close()
print("Staging cargado correctamente.")