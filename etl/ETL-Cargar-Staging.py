import duckdb
import pandas as pd

DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"
CSV_PATH = r"C:/Información/proyectos/aduana_bi/data_lake/bronze/DatosCSV.csv"
DEST_PATH = r"C:/Información/proyectos/aduana_bi/data_lake/bronze/LISTADO_DE_DESTINACIONES.xlsx"

con = duckdb.connect(DB_PATH)

# Crear esquema por si acaso
con.execute("CREATE SCHEMA IF NOT EXISTS dw;")


# ---------------------------------------------------------
# FUNCIÓN: Normalizar nombres de columnas
# ---------------------------------------------------------
def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-zA-Z0-9_]", "", regex=True)
    )
    return df

df_csv = con.execute(f"""
    SELECT * FROM read_csv_auto('{CSV_PATH}', delim=';', quote='"')
""").fetchdf()

df_csv = normalizar_columnas(df_csv)
# ---------------------------------------------------------
# CARGA DEL CSV PRINCIPAL A STAGING
# ---------------------------------------------------------

# Leer CSV con pandas para poder normalizar columnas
df_csv = pd.read_csv(
    CSV_PATH,
    sep=";",
    quotechar='"',
    dtype=str,
    on_bad_lines="skip"
)
# Normalizar columnas
df_csv = normalizar_columnas(df_csv)

# Convertir fechas si existen
for col in ["oficializacion", "cancelacion"]:
    if col in df_csv.columns:
        df_csv[col] = pd.to_datetime(df_csv[col], errors="coerce", dayfirst=True)

# Crear tabla staging limpia

con.execute("DROP TABLE IF EXISTS dw.stg_aduana;")
con.register("df_csv", df_csv)
con.execute("CREATE TABLE dw.stg_aduana AS SELECT * FROM df_csv;")

print("stg_aduana cargada correctamente.")

# ---------------------------------------------------------
# CARGA DEL EXCEL DE DESTINACIONES
# ---------------------------------------------------------

try:
    df_dest = pd.read_excel(DEST_PATH)

    # Normalizar columnas
    df_dest = normalizar_columnas(df_dest)

    # Renombrar columnas específicas
    df_dest = df_dest.rename(columns={
    "cd": "cod_destinacion",
    "descripcin": "descripcion_dest",
    "suspensivo__definitivo__temporal": "tipo_regimen_base",
    "import__export": "tipo_operacion_base"
    })

    con.execute("DROP TABLE IF EXISTS dw.stg_destinaciones;")
    con.register("df_dest", df_dest)
    con.execute("CREATE TABLE dw.stg_destinaciones AS SELECT * FROM df_dest;")

    print("stg_destinaciones cargada correctamente.")

except Exception as e:
    print("Aviso: no se cargó LISTADO_DE_DESTINACIONES.xlsx:", e)

con.close()
print("STAGING cargado correctamente.")