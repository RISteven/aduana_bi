import duckdb

# ==========================================================
# 03_cargar_dimensiones.py
# Genera todas las dimensiones desde la tabla staging
# ==========================================================

DB_PATH = r"C:\Información\proyectos\aduana_bi\db\aduana.duckdb"
con = duckdb.connect(DB_PATH)

# ----------------------------------------------------------
# DIM OPERACION
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_operacion;")
con.execute("""
INSERT INTO dw.dim_operacion (id_operacion, operacion, es_importacion, es_exportacion)
SELECT
    ROW_NUMBER() OVER (ORDER BY operacion) AS id_operacion,
    operacion,
    UPPER(TRIM(operacion)) = 'IMPORTACION' AS es_importacion,
    UPPER(TRIM(operacion)) = 'EXPORTACION' AS es_exportacion
FROM (
    SELECT DISTINCT operacion
    FROM dw.stg_aduana
    WHERE operacion IS NOT NULL
      AND TRIM(operacion) <> ''
) t;
""")

# ----------------------------------------------------------
# DIM DESTINACION
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_destinacion;")
con.execute("""
INSERT INTO dw.dim_destinacion (
    id_destinacion, cod_destinacion, descripcion_dest, tipo_regimen_base, tipo_operacion_base
)
SELECT
    ROW_NUMBER() OVER (ORDER BY s.destinacion) AS id_destinacion,
    s.destinacion AS cod_destinacion,
    d.descripcion_dest,
    d.tipo_regimen_base,
    d.tipo_operacion_base
FROM (
    SELECT DISTINCT destinacion
    FROM dw.stg_aduana
    WHERE destinacion IS NOT NULL
      AND TRIM(destinacion) <> ''
) s
LEFT JOIN dw.stg_destinaciones d
    ON TRIM(s.destinacion) = TRIM(d.cod_destinacion);
""")

# ----------------------------------------------------------
# DIM REGIMEN
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_regimen;")
con.execute("""
INSERT INTO dw.dim_regimen (id_regimen, regimen)
SELECT
    ROW_NUMBER() OVER (ORDER BY regimen) AS id_regimen,
    regimen
FROM (
    SELECT DISTINCT regimen
    FROM dw.stg_aduana
    WHERE regimen IS NOT NULL
      AND TRIM(regimen) <> ''
) t;
""")

# ----------------------------------------------------------
# DIM ADUANA
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_aduana;")
con.execute("""
INSERT INTO dw.dim_aduana (id_aduana, aduana)
SELECT
    ROW_NUMBER() OVER (ORDER BY aduana) AS id_aduana,
    aduana
FROM (
    SELECT DISTINCT aduana
    FROM dw.stg_aduana
    WHERE aduana IS NOT NULL
      AND TRIM(aduana) <> ''
) t;
""")

# ----------------------------------------------------------
# DIM PAIS
# Se arma desde país origen y país procedencia/destino
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_pais;")
con.execute("""
INSERT INTO dw.dim_pais (id_pais, codigo_pais, descripcion_pais)
SELECT
    ROW_NUMBER() OVER (ORDER BY codigo_pais, descripcion_pais) AS id_pais,
    codigo_pais,
    descripcion_pais
FROM (
    SELECT DISTINCT
        TRIM(SPLIT_PART(pais, ' - ', 1)) AS codigo_pais,
        TRIM(SPLIT_PART(pais, ' - ', 2)) AS descripcion_pais
    FROM (
        SELECT pais_origen AS pais FROM dw.stg_aduana
        UNION
        SELECT pais_procedencia_destino AS pais FROM dw.stg_aduana
    ) x
    WHERE pais IS NOT NULL
      AND TRIM(pais) <> ''
) t
WHERE codigo_pais IS NOT NULL
  AND TRIM(codigo_pais) <> '';
""")

# ----------------------------------------------------------
# DIM PRODUCTO
# La unicidad lógica es compuesta, no solo posicion_ncm
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_producto;")
con.execute("""
INSERT INTO dw.dim_producto (
    id_producto, posicion_ncm, rubro, desc_capitulo, desc_posicion, desc_partida, mercaderia
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            COALESCE(posicion, ''),
            COALESCE(rubro, ''),
            COALESCE(desc_capitulo, ''),
            COALESCE(desc_posicion, ''),
            COALESCE(desc_partida, ''),
            COALESCE(mercaderia, '')
    ) AS id_producto,
    posicion AS posicion_ncm,
    rubro,
    desc_capitulo,
    desc_posicion,
    desc_partida,
    mercaderia
FROM (
    SELECT DISTINCT
        posicion,
        rubro,
        desc_capitulo,
        desc_posicion,
        desc_partida,
        mercaderia
    FROM dw.stg_aduana
) t;
""")

# ----------------------------------------------------------
# DIM MEDIO TRANSPORTE
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_medio_transporte;")
con.execute("""
INSERT INTO dw.dim_medio_transporte (id_medio_transporte, medio_transporte)
SELECT
    ROW_NUMBER() OVER (ORDER BY medio_transporte) AS id_medio_transporte,
    medio_transporte
FROM (
    SELECT DISTINCT medio_transporte
    FROM dw.stg_aduana
    WHERE medio_transporte IS NOT NULL
      AND TRIM(medio_transporte) <> ''
) t;
""")

# ----------------------------------------------------------
# DIM CANAL
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_canal;")
con.execute("""
INSERT INTO dw.dim_canal (id_canal, canal)
SELECT
    ROW_NUMBER() OVER (ORDER BY canal) AS id_canal,
    canal
FROM (
    SELECT DISTINCT canal
    FROM dw.stg_aduana
    WHERE canal IS NOT NULL
      AND TRIM(canal) <> ''
) t;
""")

# ----------------------------------------------------------
# DIM UNIDAD MEDIDA
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_unidad_medida;")
con.execute("""
INSERT INTO dw.dim_unidad_medida (id_unidad_medida, unidad_medida)
SELECT
    ROW_NUMBER() OVER (ORDER BY unidad_medida_estadistica) AS id_unidad_medida,
    unidad_medida_estadistica AS unidad_medida
FROM (
    SELECT DISTINCT unidad_medida_estadistica
    FROM dw.stg_aduana
    WHERE unidad_medida_estadistica IS NOT NULL
      AND TRIM(unidad_medida_estadistica) <> ''
) t;
""")

# ----------------------------------------------------------
# DIM ACUERDO
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_acuerdo;")
con.execute("""
INSERT INTO dw.dim_acuerdo (id_acuerdo, acuerdo)
SELECT
    ROW_NUMBER() OVER (ORDER BY acuerdo) AS id_acuerdo,
    acuerdo
FROM (
    SELECT DISTINCT acuerdo
    FROM dw.stg_aduana
    WHERE acuerdo IS NOT NULL
      AND TRIM(acuerdo) <> ''
) t;
""")

# ----------------------------------------------------------
# DIM MARCA
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_marca;")
con.execute("""
INSERT INTO dw.dim_marca (id_marca, marca)
SELECT
    ROW_NUMBER() OVER (ORDER BY marca_item) AS id_marca,
    marca_item AS marca
FROM (
    SELECT DISTINCT marca_item
    FROM dw.stg_aduana
    WHERE marca_item IS NOT NULL
      AND TRIM(marca_item) <> ''
) t;
""")

# ----------------------------------------------------------
# DIM FECHA
# ----------------------------------------------------------
con.execute("DELETE FROM dw.dim_fecha;")
con.execute("""
INSERT INTO dw.dim_fecha (
    id_fecha, fecha, anio, mes_numero, mes_nombre, trimestre, anio_mes
)   
WITH fechas AS (
    SELECT oficializacion AS f FROM dw.stg_aduana WHERE oficializacion IS NOT NULL
    UNION
    SELECT cancelacion FROM dw.stg_aduana WHERE cancelacion IS NOT NULL
)
SELECT
    ROW_NUMBER() OVER (ORDER BY f) AS id_fecha,
    f AS fecha,
    EXTRACT(YEAR FROM f),
    EXTRACT(MONTH FROM f),
    STRFTIME(f, '%B'),
    CAST(FLOOR((EXTRACT(MONTH FROM f) - 1) / 3) + 1 AS INTEGER),
    STRFTIME(f, '%Y-%m')
FROM fechas;
""")

con.close()
print("Dimensiones generadas correctamente.")