import duckdb
import pandas as pd

DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"
CSV_PATH = r"C:/Información/proyectos/aduana_bi/data_lake/bronze/DatosCSV.csv"
DEST_PATH = r"C:/Información/proyectos/aduana_bi/data_lake/bronze/LISTADO_DE_DESTINACIONES.xlsx"

con = duckdb.connect(DB_PATH)

# Crear esquema por si acaso
con.execute("CREATE SCHEMA IF NOT EXISTS dw;")

# Cargar CSV a staging (sobrescribible)
con.execute("DROP TABLE IF EXISTS dw.stg_aduana;")
con.execute(f"""
CREATE TABLE dw.stg_aduana AS
SELECT * FROM read_csv_auto('{CSV_PATH}', delim=';', quote='"');
""")

# Normalizar fechas (si vienen como texto dd/mm/yyyy)
con.execute("""
UPDATE dw.stg_aduana
SET oficializacion = TRY_STRPTIME(CAST(oficializacion AS VARCHAR), '%d/%m/%Y'),
    cancelacion    = TRY_STRPTIME(CAST(cancelacion AS VARCHAR), '%d/%m/%Y');
""")

# Cargar destinaciones a staging (si usás el Excel)
try:
    df_dest = pd.read_excel(DEST_PATH)

    df_dest = df_dest.rename(columns={
        "CÓD.": "cod_destinacion",
        "DESCRIPCIÓN": "descripcion_dest",
        "SUSPENSIVO - DEFINITIVO - TEMPORAL": "tipo_regimen_base",
        "IMPORT / EXPORT": "tipo_operacion_base"
    })

    con.execute("DROP TABLE IF EXISTS dw.stg_destinaciones;")
    con.execute("""
        CREATE TABLE dw.stg_destinaciones (
            cod_destinacion VARCHAR,
            descripcion_dest VARCHAR,
            tipo_regimen_base VARCHAR,
            tipo_operacion_base VARCHAR
        );
    """)
    con.register("df_dest", df_dest)
    con.execute("INSERT INTO dw.stg_destinaciones SELECT * FROM df_dest;")
    print("stg_destinaciones cargada correctamente.")
except Exception as e:
    print("Aviso: no se cargó LISTADO_DE_DESTINACIONES.xlsx:", e)

con.close()
print("STAGING cargado correctamente.")