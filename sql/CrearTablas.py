import duckdb
# DB_PATH = "../db/aduana.duckdb"
DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"
con = duckdb.connect(DB_PATH)

sql = """
CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.stg_aduana (
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
    pais_destino VARCHAR,
    uso VARCHAR,
    unidad_medida_est VARCHAR,
    cantidad_estadistica DOUBLE,
    kilo_neto DOUBLE,
    kilo_bruto DOUBLE,
    fob_usd DOUBLE,
    flete_usd DOUBLE,
    seguro_usd DOUBLE,
    imponible_usd DOUBLE,
    imponible_gs DOUBLE,
    ajuste_incluir DOUBLE,
    ajuste_deducir DOUBLE,
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

CREATE TABLE IF NOT EXISTS dw.dim_operacion (
    id_operacion INTEGER PRIMARY KEY,
    operacion VARCHAR,
    es_importacion BOOLEAN,
    es_exportacion BOOLEAN
);

CREATE TABLE IF NOT EXISTS dw.dim_destinacion (
    id_destinacion INTEGER,
    cod_destinacion VARCHAR,
    descripcion_dest VARCHAR,
    tipo_regimen_base VARCHAR,
    tipo_operacion_base VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_regimen (
    id_regimen INTEGER,
    regimen VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_aduana (
    id_aduana INTEGER,
    aduana VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_pais (
    id_pais INTEGER,
    codigo_pais VARCHAR,
    descripcion_pais VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_producto (
    id_producto INTEGER,
    posicion_ncm VARCHAR,
    rubro VARCHAR,
    desc_capitulo VARCHAR,
    desc_posicion VARCHAR,
    desc_partida VARCHAR,
    mercaderia VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_medio_transporte (
    id_medio_transporte INTEGER,
    medio_transporte VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_canal (
    id_canal INTEGER,
    canal VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_unidad_medida (
    id_unidad_medida INTEGER,
    unidad_medida VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_acuerdo (
    id_acuerdo INTEGER,
    acuerdo VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_marca (
    id_marca INTEGER,
    marca VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.dim_fecha (
    id_fecha INTEGER,
    fecha DATE,
    anio INTEGER,
    mes_numero INTEGER,
    mes_nombre VARCHAR,
    trimestre INTEGER,
    anio_mes VARCHAR
);

CREATE TABLE IF NOT EXISTS dw.fact_aduana_item (
    id_fact INTEGER,
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
    fob_usd DOUBLE,
    flete_usd DOUBLE,
    seguro_usd DOUBLE,
    imponible_usd DOUBLE,
    imponible_gs DOUBLE,
    ajuste_incluir DOUBLE,
    ajuste_deducir DOUBLE,
    total DOUBLE
);
"""

con.execute(sql)
con.close()

print("Tablas creadas correctamente.")