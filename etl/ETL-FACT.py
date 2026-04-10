import duckdb
import pandas as pd


DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"
con = duckdb.connect(DB_PATH)

# Limpiar FACT
con.execute("DELETE FROM dw.fact_aduana_item;")

# Cargar FACT
con.execute("""
INSERT INTO dw.fact_aduana_item (
    id_fact,
    despacho_cifrado, item,
    id_operacion, id_destinacion, id_regimen, id_aduana,
    id_pais_origen, id_pais_destino, id_producto,
    id_medio_transporte, id_canal, id_unidad_medida,
    id_acuerdo, id_marca,
    id_fecha_oficializacion, id_fecha_cancelacion,
    uso,
    cantidad_estadistica, kilo_neto, kilo_bruto,
    fob_usd, flete_usd, seguro_usd,
    imponible_usd, imponible_gs,
    ajuste_incluir, ajuste_deducir,
    total
)
SELECT
    ROW_NUMBER() OVER () AS id_fact,
    s.despacho_cifrado,
    s.item,

    o.id_operacion,
    d.id_destinacion,
    r.id_regimen,
    a.id_aduana,

    po.id_pais AS id_pais_origen,
    pd.id_pais AS id_pais_destino,
    p.id_producto,

    mt.id_medio_transporte,
    c.id_canal,
    um.id_unidad_medida,

    ac.id_acuerdo,
    m.id_marca,

    fo.id_fecha AS id_fecha_oficializacion,
    fc.id_fecha AS id_fecha_cancelacion,

    s.uso,

    s.cantidad_estadistica,
    s.kilo_neto,
    s.kilo_bruto,
    s.fob_dolar,
    s.flete_dolar,
    s.seguro_dolar,
    s.imponible_dolar,
    s.imponible_gs,
    s.ajuste_a_incluir,
    s.ajuste_a_deducir,
    s.total

FROM dw.stg_aduana s
LEFT JOIN dw.dim_operacion o
    ON s.operacion = o.operacion
LEFT JOIN dw.dim_destinacion d
    ON s.destinacion = d.cod_destinacion
LEFT JOIN dw.dim_regimen r
    ON s.regimen = r.regimen
LEFT JOIN dw.dim_aduana a
    ON s.aduana = a.aduana

LEFT JOIN dw.dim_pais po
    ON SPLIT_PART(s.pais_origen, ' - ', 1) = po.codigo_pais
LEFT JOIN dw.dim_pais pd
    ON SPLIT_PART(s.pais_procedenciadestino, ' - ', 1) = pd.codigo_pais

LEFT JOIN dw.dim_producto p
    ON s.posicion = p.posicion_ncm
   AND s.rubro = p.rubro
   AND s.desc_capitulo = p.desc_capitulo

LEFT JOIN dw.dim_medio_transporte mt
    ON s.medio_transporte = mt.medio_transporte
LEFT JOIN dw.dim_canal c
    ON s.canal = c.canal
LEFT JOIN dw.dim_unidad_medida um
    ON s.unidad_medida_estadistica = um.unidad_medida
LEFT JOIN dw.dim_acuerdo ac
    ON s.acuerdo = ac.acuerdo
LEFT JOIN dw.dim_marca m
    ON s.marca_item = m.marca

LEFT JOIN dw.dim_fecha fo
    ON s.oficializacion = fo.fecha
LEFT JOIN dw.dim_fecha fc
    ON s.cancelacion = fc.fecha;
""")

con.close()
print("FACT TABLE generada correctamente.")