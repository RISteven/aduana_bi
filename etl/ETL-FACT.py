import duckdb

# ==========================================================
# 04_cargar_fact.py
# Carga la tabla de hechos desde staging y dimensiones
# ==========================================================

DB_PATH = r"C:\Información\proyectos\aduana_bi\db\aduana.duckdb"
con = duckdb.connect(DB_PATH)

con.execute("DELETE FROM dw.fact_aduana_item;")

con.execute("""
INSERT INTO dw.fact_aduana_item (
    id_fact,
    despacho_cifrado,
    item,
    id_operacion,
    id_destinacion,
    id_regimen,
    id_aduana,
    id_pais_origen,
    id_pais_destino,
    id_producto,
    id_medio_transporte,
    id_canal,
    id_unidad_medida,
    id_acuerdo,
    id_marca,
    id_fecha_oficializacion,
    id_fecha_cancelacion,
    uso,
    cantidad_estadistica,
    kilo_neto,
    kilo_bruto,
    fob_dolar,
    flete_dolar,
    seguro_dolar,
    imponible_dolar,
    imponible_gs,
    ajuste_a_incluir,
    ajuste_a_deducir,
    derecho,
    isc,
    servicio,
    renta,
    iva,
    otros,
    total
)
SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            COALESCE(s.despacho_cifrado, ''),
            COALESCE(s.item, 0)
    ) AS id_fact,

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
    s.derecho,
    s.isc,
    s.servicio,
    s.renta,
    s.iva,
    s.otros,
    s.total
FROM dw.stg_aduana s
LEFT JOIN dw.dim_operacion o
    ON TRIM(s.operacion) = TRIM(o.operacion)
LEFT JOIN dw.dim_destinacion d
    ON TRIM(s.destinacion) = TRIM(d.cod_destinacion)
LEFT JOIN dw.dim_regimen r
    ON TRIM(s.regimen) = TRIM(r.regimen)
LEFT JOIN dw.dim_aduana a
    ON TRIM(s.aduana) = TRIM(a.aduana)

LEFT JOIN dw.dim_pais po
    ON TRIM(SPLIT_PART(s.pais_origen, ' - ', 1)) = TRIM(po.codigo_pais)
LEFT JOIN dw.dim_pais pd
    ON TRIM(SPLIT_PART(s.pais_procedencia_destino, ' - ', 1)) = TRIM(pd.codigo_pais)

LEFT JOIN dw.dim_producto p
    ON COALESCE(TRIM(s.posicion), '') = COALESCE(TRIM(p.posicion_ncm), '')
   AND COALESCE(TRIM(s.rubro), '') = COALESCE(TRIM(p.rubro), '')
   AND COALESCE(TRIM(s.desc_capitulo), '') = COALESCE(TRIM(p.desc_capitulo), '')
   AND COALESCE(TRIM(s.desc_posicion), '') = COALESCE(TRIM(p.desc_posicion), '')
   AND COALESCE(TRIM(s.desc_partida), '') = COALESCE(TRIM(p.desc_partida), '')
   AND COALESCE(TRIM(s.mercaderia), '') = COALESCE(TRIM(p.mercaderia), '')

LEFT JOIN dw.dim_medio_transporte mt
    ON TRIM(s.medio_transporte) = TRIM(mt.medio_transporte)
LEFT JOIN dw.dim_canal c
    ON TRIM(s.canal) = TRIM(c.canal)
LEFT JOIN dw.dim_unidad_medida um
    ON TRIM(s.unidad_medida_estadistica) = TRIM(um.unidad_medida)
LEFT JOIN dw.dim_acuerdo ac
    ON TRIM(s.acuerdo) = TRIM(ac.acuerdo)
LEFT JOIN dw.dim_marca m
    ON TRIM(s.marca_item) = TRIM(m.marca)

LEFT JOIN dw.dim_fecha fo
    ON s.oficializacion = fo.fecha
LEFT JOIN dw.dim_fecha fc
    ON s.cancelacion = fc.fecha

WHERE s.despacho_cifrado IS NOT NULL
  AND s.item IS NOT NULL;
""")

con.close()
print("Fact table generada correctamente.")