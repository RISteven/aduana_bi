import duckdb

# Conectar o crear la base de datos DuckDB
con = duckdb.connect('aduana.duckdb')

# Sentencias SQL para crear tablas
sql_create_tables = """
CREATE TABLE dim_operacion (
    id_operacion INTEGER PRIMARY KEY,
    descripcion VARCHAR
);
CREATE TABLE dim_destinacion (
    id_destinacion INTEGER PRIMARY KEY,
    descripcion VARCHAR
);
-- Agrega aquí el resto de tablas según el modelo estrella
CREATE TABLE fact_aduana_item (
    id_operacion INTEGER,
    id_destinacion INTEGER,
    -- otros campos...
    cantidad NUMERIC,
    valor_fob NUMERIC,
    valor_cif NUMERIC
);
"""

# Ejecutar las sentencias
con.execute(sql_create_tables)

# Cerrar conexión
con.close()