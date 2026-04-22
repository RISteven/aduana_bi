
import duckdb
import os

# ==========================================================
# CONFIGURACIÓN DE RUTA (AJUSTA SI ES NECESARIO)
# ==========================================================
DB_PATH = r"C:\Información\proyectos\aduana_bi\db\aduana.duckdb"

# Crear carpeta si no existe (evita error de ruta)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Conexión
con = duckdb.connect(DB_PATH)

print("Creando estructura DW...")

# ==========================================================
# SCHEMA
# ==========================================================
con.execute("CREATE SCHEMA IF NOT EXISTS dw;")

# ==========================================================
# LIMPIEZA
# ==========================================================
con.execute("DROP TABLE IF EXISTS dw.fact_aduana_item;")
con.execute("DROP TABLE IF EXISTS dw.dim_operacion;")
con.execute("DROP TABLE IF EXISTS dw.dim_destinacion;")
con.execute("DROP TABLE IF EXISTS dw.dim_regimen;")
con.execute("DROP TABLE IF EXISTS dw.dim_aduana;")
con.execute("DROP TABLE IF EXISTS dw.dim_pais;")
con.execute("DROP TABLE IF EXISTS dw.dim_producto;")
con.execute("DROP TABLE IF EXISTS dw.dim_medio_transporte;")
con.execute("DROP TABLE IF EXISTS dw.dim_canal;")
con.execute("DROP TABLE IF EXISTS dw.dim_unidad_medida;")
con.execute("DROP TABLE IF EXISTS dw.dim_acuerdo;")
con.execute("DROP TABLE IF EXISTS dw.dim_marca;")
con.execute("DROP TABLE IF EXISTS dw.dim_fecha;")
con.execute("DROP TABLE IF EXISTS dw.stg_destinaciones;")
con.execute("DROP TABLE IF EXISTS dw.stg_aduana;")

# ==========================================================
# STAGING
# ==========================================================
con.execute("""
CREATE TABLE dw.stg_aduana (
    despacho_cifrado VARCHAR,
    operacion VARCHAR,
    destinacion VARCHAR,
    regimen VARCHAR,
    oficializacion DATE,
    cancelacion DATE,
    anio INTEGER,
    mes VARCHAR,
    aduana VARCHAR,
    cotizacion DOUBLE,
    medio_transporte VARCHAR,
    canal VARCHAR,
    item INTEGER,
    pais_origen VARCHAR,
    pais_procedencia_destino VARCHAR,
    uso VARCHAR,
    unidad_medida_estadistica VARCHAR,
    cantidad_estadistica DOUBLE,
    kilo_neto DOUBLE,
    kilo_bruto DOUBLE,
    fob_dolar DOUBLE,
    flete_dolar DOUBLE,
    seguro_dolar DOUBLE,
    imponible_dolar DOUBLE,
    imponible_gs DOUBLE,
    ajuste_a_incluir DOUBLE,
    ajuste_a_deducir DOUBLE,
    posicion VARCHAR,
    rubro VARCHAR,
    desc_capitulo VARCHAR,
    desc_posicion VARCHAR,
    desc_partida VARCHAR,
    mercaderia VARCHAR,
    marca_item VARCHAR,
    acuerdo VARCHAR,
    derecho DOUBLE,
    isc DOUBLE,
    servicio DOUBLE,
    renta DOUBLE,
    iva DOUBLE,
    otros DOUBLE,
    total DOUBLE
);
""")

con.execute("""
CREATE TABLE dw.stg_destinaciones (
    cod_destinacion VARCHAR,
    descripcion_dest VARCHAR,
    tipo_regimen_base VARCHAR,
    tipo_operacion_base VARCHAR
);
""")

# ==========================================================
# DIMENSIONES
# ==========================================================
con.execute("""
CREATE TABLE dw.dim_operacion (
    id_operacion INTEGER PRIMARY KEY,
    operacion VARCHAR UNIQUE,
    es_importacion BOOLEAN,
    es_exportacion BOOLEAN
);
""")

con.execute("""
CREATE TABLE dw.dim_destinacion (
    id_destinacion INTEGER PRIMARY KEY,
    cod_destinacion VARCHAR UNIQUE,
    descripcion_dest VARCHAR,
    tipo_regimen_base VARCHAR,
    tipo_operacion_base VARCHAR
);
""")

con.execute("""
CREATE TABLE dw.dim_regimen (
    id_regimen INTEGER PRIMARY KEY,
    regimen VARCHAR UNIQUE
);
""")

con.execute("""
CREATE TABLE dw.dim_aduana (
    id_aduana INTEGER PRIMARY KEY,
    aduana VARCHAR UNIQUE
);
""")

con.execute("""
CREATE TABLE dw.dim_pais (
    id_pais INTEGER PRIMARY KEY,
    codigo_pais VARCHAR UNIQUE,
    descripcion_pais VARCHAR
);
""")

con.execute("""
CREATE TABLE dw.dim_producto (
    id_producto INTEGER PRIMARY KEY,
    posicion_ncm VARCHAR,
    rubro VARCHAR,
    desc_capitulo VARCHAR,
    desc_posicion VARCHAR,
    desc_partida VARCHAR,
    mercaderia VARCHAR
);
""")

con.execute("""
CREATE TABLE dw.dim_medio_transporte (
    id_medio_transporte INTEGER PRIMARY KEY,
    medio_transporte VARCHAR UNIQUE
);
""")

con.execute("""
CREATE TABLE dw.dim_canal (
    id_canal INTEGER PRIMARY KEY,
    canal VARCHAR UNIQUE
);
""")

con.execute("""
CREATE TABLE dw.dim_unidad_medida (
    id_unidad_medida INTEGER PRIMARY KEY,
    unidad_medida VARCHAR UNIQUE
);
""")

con.execute("""
CREATE TABLE dw.dim_acuerdo (
    id_acuerdo INTEGER PRIMARY KEY,
    acuerdo VARCHAR UNIQUE
);
""")

con.execute("""
CREATE TABLE dw.dim_marca (
    id_marca INTEGER PRIMARY KEY,
    marca VARCHAR UNIQUE
);
""")

con.execute("""
CREATE TABLE dw.dim_fecha (
    id_fecha INTEGER PRIMARY KEY,
    fecha DATE UNIQUE,
    anio INTEGER,
    mes_numero INTEGER,
    mes_nombre VARCHAR,
    trimestre INTEGER,
    anio_mes VARCHAR
);
""")

# ==========================================================
# FACT TABLE
# ==========================================================
con.execute("""
CREATE TABLE dw.fact_aduana_item (
    id_fact BIGINT PRIMARY KEY,
    despacho_cifrado VARCHAR,
    item INTEGER,

    id_operacion INTEGER,
    id_destinacion INTEGER,
    id_regimen INTEGER,
    id_aduana INTEGER,
    id_pais_origen INTEGER,
    id_pais_destino INTEGER,
    id_producto INTEGER,
    id_medio_transporte INTEGER,
    id_canal INTEGER,
    id_unidad_medida INTEGER,
    id_acuerdo INTEGER,
    id_marca INTEGER,
    id_fecha_oficializacion INTEGER,
    id_fecha_cancelacion INTEGER,

    uso VARCHAR,
    cantidad_estadistica DOUBLE,
    kilo_neto DOUBLE,
    kilo_bruto DOUBLE,
    fob_dolar DOUBLE,
    flete_dolar DOUBLE,
    seguro_dolar DOUBLE,
    imponible_dolar DOUBLE,
    imponible_gs DOUBLE,
    ajuste_a_incluir DOUBLE,
    ajuste_a_deducir DOUBLE,
    derecho DOUBLE,
    isc DOUBLE,
    servicio DOUBLE,
    renta DOUBLE,
    iva DOUBLE,
    otros DOUBLE,
    total DOUBLE,

    UNIQUE(despacho_cifrado, item)
);
""")

# ==========================================================
# CIERRE
# ==========================================================
con.close()

print("DW creado correctamente sin errores.")