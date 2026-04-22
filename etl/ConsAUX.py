import duckdb

# ==========================================================
# 05_validar_dw.py
# Valida estructura, conteos, duplicados y claves huérfanas
# ==========================================================

DB_PATH = r"C:\Información\proyectos\aduana_bi\db\aduana.duckdb"
con = duckdb.connect(DB_PATH)

print("\n==============================")
print(" VALIDACION DEL MODELO DW ")
print("==============================\n")

# ----------------------------------------------------------
# 1. Tablas existentes
# ----------------------------------------------------------
print("1) Tablas encontradas en el esquema dw:\n")
tables = con.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'dw'
    ORDER BY table_name;
""").fetchall()

for t in tables:
    print(" -", t[0])

# ----------------------------------------------------------
# 2. Conteo por tabla
# ----------------------------------------------------------
print("\n2) Conteo de filas por tabla:\n")
for t in tables:
    table_name = t[0]
    count = con.execute(f"SELECT COUNT(*) FROM dw.{table_name};").fetchone()[0]
    print(f" - {table_name}: {count} filas")

# ----------------------------------------------------------
# 3. Validar duplicados en fact por clave natural
# ----------------------------------------------------------
print("\n3) Duplicados en fact_aduana_item por (despacho_cifrado, item):\n")
dup_fact = con.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT despacho_cifrado, item, COUNT(*) c
        FROM dw.fact_aduana_item
        GROUP BY despacho_cifrado, item
        HAVING COUNT(*) > 1
    ) x;
""").fetchone()[0]
print(f" - Duplicados: {dup_fact}")

# ----------------------------------------------------------
# 4. Nulos en clave natural de fact
# ----------------------------------------------------------
print("\n4) Nulos en campos clave de fact:\n")
nulls_fact = con.execute("""
    SELECT
        SUM(CASE WHEN despacho_cifrado IS NULL THEN 1 ELSE 0 END) AS null_despacho,
        SUM(CASE WHEN item IS NULL THEN 1 ELSE 0 END) AS null_item
    FROM dw.fact_aduana_item;
""").fetchone()
print(f" - despacho_cifrado NULL: {nulls_fact[0]}")
print(f" - item NULL: {nulls_fact[1]}")

# ----------------------------------------------------------
# 5. Validación de claves foráneas huérfanas
# ----------------------------------------------------------
print("\n5) Detección de claves huérfanas:\n")

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
    print(f" - {fk} -> {dim}: {orphan_count} huérfanas")

# ----------------------------------------------------------
# 6. Duplicados en dimensiones
# ----------------------------------------------------------
print("\n6) Duplicados en dimensiones por clave natural:\n")

dim_keys = {
    "dim_operacion": "operacion",
    "dim_destinacion": "cod_destinacion",
    "dim_regimen": "regimen",
    "dim_aduana": "aduana",
    "dim_pais": "codigo_pais",
    "dim_medio_transporte": "medio_transporte",
    "dim_canal": "canal",
    "dim_unidad_medida": "unidad_medida",
    "dim_acuerdo": "acuerdo",
    "dim_marca": "marca",
    "dim_fecha": "fecha"
}

for dim, natural_key in dim_keys.items():
    dup = con.execute(f"""
        SELECT COUNT(*)
        FROM (
            SELECT {natural_key}, COUNT(*) c
            FROM dw.{dim}
            GROUP BY {natural_key}
            HAVING COUNT(*) > 1
        ) x;
    """).fetchone()[0]
    print(f" - {dim}: {dup} duplicados")

# ----------------------------------------------------------
# 7. Validación especial de producto
# ----------------------------------------------------------
print("\n7) Duplicados lógicos en dim_producto:\n")

dup_producto = con.execute("""
    SELECT COUNT(*)
    FROM (
        SELECT
            posicion_ncm,
            rubro,
            desc_capitulo,
            desc_posicion,
            desc_partida,
            mercaderia,
            COUNT(*) c
        FROM dw.dim_producto
        GROUP BY
            posicion_ncm,
            rubro,
            desc_capitulo,
            desc_posicion,
            desc_partida,
            mercaderia
        HAVING COUNT(*) > 1
    ) x;
""").fetchone()[0]

print(f" - dim_producto: {dup_producto} duplicados lógicos")

# ----------------------------------------------------------
# 8. Validación básica del staging
# ----------------------------------------------------------
print("\n8) Validación básica del staging:\n")
stg_check = con.execute("""
    SELECT
        COUNT(*) AS total_filas,
        SUM(CASE WHEN despacho_cifrado IS NULL THEN 1 ELSE 0 END) AS null_despacho,
        SUM(CASE WHEN item IS NULL THEN 1 ELSE 0 END) AS null_item,
        SUM(CASE WHEN oficializacion IS NULL THEN 1 ELSE 0 END) AS null_oficializacion
    FROM dw.stg_aduana;
""").fetchone()

print(f" - Total filas staging: {stg_check[0]}")
print(f" - despacho_cifrado NULL: {stg_check[1]}")
print(f" - item NULL: {stg_check[2]}")
print(f" - oficializacion NULL: {stg_check[3]}")

con.close()
print("\nValidación completada.")