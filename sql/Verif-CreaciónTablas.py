import duckdb
import pandas as pd
DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"
con = duckdb.connect(DB_PATH)

print("\n==============================")
print(" VERIFICACIÓN DEL MODELO DW ")
print("==============================\n")

# -----------------------------
# 1. Verificar existencia de tablas
# -----------------------------
print("1) Tablas encontradas en el esquema 'dw':\n")
tables = con.execute("""
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema = 'dw'
    ORDER BY table_name;
""").fetchdf()
print(tables, "\n")

# -----------------------------
# 2. Conteo de filas por tabla
# -----------------------------
print("2) Conteo de filas por tabla:\n")
for t in tables["table_name"]:
    count = con.execute(f"SELECT COUNT(*) FROM dw.{t};").fetchone()[0]
    print(f" - {t}: {count} filas")
print()

# -----------------------------
# 3. Validación de claves foráneas en fact table
# -----------------------------
print("3) Validación de claves foráneas en fact_aduana_item:\n")

fk_checks = {
    "id_operacion": "dim_operacion",
    "id_destinacion": "dim_destinacion",
    "id_regimen": "dim_regimen",
    "id_aduana": "dim_aduana",
    "id_pais_origen": "dim_pais",
    "id_pais_destino": "dim_pais",
    "id_producto": "dim_producto",
    "id_medio_transporte": "dim_medio_transporte",
    "id_canal": "dim_canal",
    "id_unidad_medida": "dim_unidad_medida",
    "id_acuerdo": "dim_acuerdo",
    "id_marca": "dim_marca",
    "id_fecha_oficializacion": "dim_fecha",
    "id_fecha_cancelacion": "dim_fecha"
}

for fk, dim in fk_checks.items():
    nulls = con.execute(f"""
        SELECT COUNT(*) 
        FROM dw.fact_aduana_item 
        WHERE {fk} IS NULL;
    """).fetchone()[0]

    print(f" - {fk}: {nulls} valores NULL")

print()

# -----------------------------
# 4. Detección de claves huérfanas
# -----------------------------
print("4) Detección de claves huérfanas:\n")

# Mapeo FK → (dimensión, PK real)
fk_dim_pk = {
    "id_operacion": ("dim_operacion", "id_operacion"),
    "id_destinacion": ("dim_destinacion", "id_destinacion"),
    "id_regimen": ("dim_regimen", "id_regimen"),
    "id_aduana": ("dim_aduana", "id_aduana"),
    "id_pais_origen": ("dim_pais", "id_pais"),
    "id_pais_destino": ("dim_pais", "id_pais"),
    "id_producto": ("dim_producto", "id_producto"),
    "id_medio_transporte": ("dim_medio_transporte", "id_medio_transporte"),
    "id_canal": ("dim_canal", "id_canal"),
    "id_unidad_medida": ("dim_unidad_medida", "id_unidad_medida"),
    "id_acuerdo": ("dim_acuerdo", "id_acuerdo"),
    "id_marca": ("dim_marca", "id_marca"),
    "id_fecha_oficializacion": ("dim_fecha", "id_fecha"),
    "id_fecha_cancelacion": ("dim_fecha", "id_fecha")
}

for fk, (dim, pk) in fk_dim_pk.items():
    query = f"""
        SELECT COUNT(*)
        FROM dw.fact_aduana_item f
        LEFT JOIN dw.{dim} d
            ON f.{fk} = d.{pk}
        WHERE f.{fk} IS NOT NULL
          AND d.{pk} IS NULL;
    """
    orphan_count = con.execute(query).fetchone()[0]
    print(f" - {fk} → {dim}: {orphan_count} claves huérfanas")

print()

# -----------------------------
# 5. Validación de duplicados en dimensiones
# -----------------------------
print("5) Duplicados en dimensiones:\n")

dim_keys = {
    "dim_operacion": "operacion",
    "dim_destinacion": "cod_destinacion",
    "dim_regimen": "regimen",
    "dim_aduana": "aduana",
    "dim_pais": "codigo_pais",
    "dim_producto": "posicion_ncm",
    "dim_medio_transporte": "medio_transporte",
    "dim_canal": "canal",
    "dim_unidad_medida": "unidad_medida",
    "dim_acuerdo": "acuerdo",
    "dim_marca": "marca",
}

for dim, natural_key in dim_keys.items():
    dup = con.execute(f"""
        SELECT COUNT(*) 
        FROM (
            SELECT {natural_key}, COUNT(*) c
            FROM dw.{dim}
            GROUP BY {natural_key}
            HAVING COUNT(*) > 1
        );
    """).fetchone()[0]

    print(f" - {dim}: {dup} duplicados en {natural_key}")

print()

# -----------------------------
# 6. Validación de fechas
# -----------------------------
print("6) Validación de fechas:\n")

invalid_dates = con.execute("""
    SELECT COUNT(*)
    FROM dw.dim_fecha
    WHERE fecha IS NULL;
""").fetchone()[0]

print(f" - Fechas inválidas en dim_fecha: {invalid_dates}\n")

# -----------------------------
# 7. Validación del staging
# -----------------------------
print("7) Validación del staging:\n")

stg_nulls = con.execute("""
    SELECT 
        SUM(CASE WHEN despacho_cifrado IS NULL THEN 1 ELSE 0 END) AS null_despacho,
        SUM(CASE WHEN item IS NULL THEN 1 ELSE 0 END) AS null_item
    FROM dw.stg_aduana;
""").fetchdf()

print(stg_nulls, "\n")

# -----------------------------
# 7. Validación del staging
# -----------------------------
print("8) Validación de Fecha:\n")

dim_fec = con.execute("""
SELECT COUNT(*) FROM dw.stg_aduana WHERE oficializacion IS NOT NULL;
SELECT COUNT(DISTINCT oficializacion) FROM dw.stg_aduana; """).fetchdf()

print(dim_fec, "\n")
con.close()

print("Verificación completada.\n")