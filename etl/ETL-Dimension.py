import duckdb

DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"
con = duckdb.connect(DB_PATH)

# Dim Operación
con.execute("DELETE FROM dw.dim_operacion;")
con.execute("""
INSERT INTO dw.dim_operacion (id_operacion, operacion, es_importacion, es_exportacion)
SELECT
    ROW_NUMBER() OVER () AS id_operacion,
    operacion,
    UPPER(operacion) = 'IMPORTACION' AS es_importacion,
    UPPER(operacion) = 'EXPORTACION' AS es_exportacion
FROM (
    SELECT DISTINCT operacion
    FROM dw.stg_aduana
    WHERE operacion IS NOT NULL
) t;
""")

# Dim Destinación
con.execute("DELETE FROM dw.dim_destinacion;")
con.execute("""
INSERT INTO dw.dim_destinacion (
    id_destinacion, cod_destinacion, descripcion_dest, tipo_regimen_base, tipo_operacion_base
)
SELECT
    ROW_NUMBER() OVER () AS id_destinacion,
    s.destinacion AS cod_destinacion,
    d.descripcion_dest,
    d.tipo_regimen_base,
    d.tipo_operacion_base
FROM (
    SELECT DISTINCT destinacion
    FROM dw.stg_aduana
    WHERE destinacion IS NOT NULL
) s
LEFT JOIN dw.stg_destinaciones d
    ON s.destinacion = d.cod_destinacion;
""")

# Dim Régimen
con.execute("DELETE FROM dw.dim_regimen;")
con.execute("""
INSERT INTO dw.dim_regimen (id_regimen, regimen)
SELECT
    ROW_NUMBER() OVER () AS id_regimen,
    regimen
FROM (
    SELECT DISTINCT regimen
    FROM dw.stg_aduana
    WHERE regimen IS NOT NULL
) t;
""")

# Dim Aduana
con.execute("DELETE FROM dw.dim_aduana;")
con.execute("""
INSERT INTO dw.dim_aduana (id_aduana, aduana)
SELECT
    ROW_NUMBER() OVER () AS id_aduana,
    aduana
FROM (
    SELECT DISTINCT aduana
    FROM dw.stg_aduana
    WHERE aduana IS NOT NULL
) t;
""")

# Dim País
con.execute("DELETE FROM dw.dim_pais;")
con.execute("""
INSERT INTO dw.dim_pais (id_pais, codigo_pais, descripcion_pais)
SELECT
    ROW_NUMBER() OVER () AS id_pais,
    codigo_pais,
    descripcion_pais
FROM (
    SELECT DISTINCT
    SPLIT_PART(pais, ' - ', 1) AS codigo_pais,
    SPLIT_PART(pais, ' - ', 2) AS descripcion_pais
FROM (
    SELECT pais_origen AS pais FROM dw.stg_aduana
    UNION
    SELECT pais_procedenciadestino AS pais FROM dw.stg_aduana
) x
WHERE pais IS NOT NULL
) t;
""")

# Dim Producto
con.execute("DELETE FROM dw.dim_producto;")
con.execute("""
INSERT INTO dw.dim_producto (
    id_producto, posicion_ncm, rubro, desc_capitulo, desc_posicion, desc_partida, mercaderia
)
SELECT
    ROW_NUMBER() OVER () AS id_producto,
    posicion,
    rubro,
    desc_capitulo,
    desc_posicion,
    desc_partida,
    mercaderia
FROM (
    SELECT DISTINCT
        posicion, rubro, desc_capitulo, desc_posicion, desc_partida, mercaderia
    FROM dw.stg_aduana
) t;
""")

# Dim Medio Transporte
con.execute("DELETE FROM dw.dim_medio_transporte;")
con.execute("""
INSERT INTO dw.dim_medio_transporte (id_medio_transporte, medio_transporte)
SELECT
    ROW_NUMBER() OVER () AS id_medio_transporte,
    medio_transporte
FROM (
    SELECT DISTINCT medio_transporte
    FROM dw.stg_aduana
    WHERE medio_transporte IS NOT NULL
) t;
""")

# Dim Canal
con.execute("DELETE FROM dw.dim_canal;")
con.execute("""
INSERT INTO dw.dim_canal (id_canal, canal)
SELECT
    ROW_NUMBER() OVER () AS id_canal,
    canal
FROM (
    SELECT DISTINCT canal
    FROM dw.stg_aduana
    WHERE canal IS NOT NULL
) t;
""")

# Dim Unidad Medida
con.execute("DELETE FROM dw.dim_unidad_medida;")
con.execute("""
INSERT INTO dw.dim_unidad_medida (id_unidad_medida, unidad_medida)
SELECT
    ROW_NUMBER() OVER () AS id_unidad_medida,
    unidad_medida_estadistica
FROM (
    SELECT DISTINCT unidad_medida_estadistica
    FROM dw.stg_aduana
    WHERE unidad_medida_estadistica IS NOT NULL
) t;
""")

# Dim Acuerdo
con.execute("DELETE FROM dw.dim_acuerdo;")
con.execute("""
INSERT INTO dw.dim_acuerdo (id_acuerdo, acuerdo)
SELECT
    ROW_NUMBER() OVER () AS id_acuerdo,
    acuerdo
FROM (
    SELECT DISTINCT acuerdo
    FROM dw.stg_aduana
    WHERE acuerdo IS NOT NULL
) t;
""")

# Dim Marca
con.execute("DELETE FROM dw.dim_marca;")
con.execute("""
INSERT INTO dw.dim_marca (id_marca, marca)
SELECT
    ROW_NUMBER() OVER () AS id_marca,
    marca_item
FROM (
    SELECT DISTINCT marca_item
    FROM dw.stg_aduana
    WHERE marca_item IS NOT NULL
) t;
""")

# Dim Fecha
con.execute("DELETE FROM dw.dim_fecha;")
con.execute("""
INSERT INTO dw.dim_fecha (
    id_fecha, fecha, anio, mes_numero, mes_nombre, trimestre, anio_mes
)
SELECT
    ROW_NUMBER() OVER () AS id_fecha,
    f AS fecha,
    EXTRACT(YEAR FROM f) AS anio,
    EXTRACT(MONTH FROM f) AS mes_numero,
    STRFTIME(f, '%B') AS mes_nombre,
    ((EXTRACT(MONTH FROM f)-1)/3)+1 AS trimestre,
    STRFTIME(f, '%Y-%m') AS anio_mes
FROM (
    SELECT oficializacion AS f FROM dw.stg_aduana
    UNION
    SELECT cancelacion AS f FROM dw.stg_aduana
) x
WHERE f IS NOT NULL;
""")

con.close()
print("DIMENSIONES generadas correctamente.")