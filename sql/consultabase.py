# import duckdb
# con = duckdb.connect("aduana.duckdb")
# con.execute("SELECT 1").fetchall()

con.execute("""
ALTER TABLE dw.stg_aduana RENAME COLUMN "PAIS ORIGEN" TO pais_origen;
ALTER TABLE dw.stg_aduana RENAME COLUMN "PAIS DESTINO" TO pais_destino;
ALTER TABLE dw.stg_aduana RENAME COLUMN "UNIDAD MEDIDA EST" TO unidad_medida_est;
ALTER TABLE dw.stg_aduana RENAME COLUMN "CANTIDAD ESTADISTICA" TO cantidad_estadistica;
ALTER TABLE dw.stg_aduana RENAME COLUMN "KILO NETO" TO kilo_neto;
ALTER TABLE dw.stg_aduana RENAME COLUMN "KILO BRUTO" TO kilo_bruto;
ALTER TABLE dw.stg_aduana RENAME COLUMN "FOB USD" TO fob_usd;
ALTER TABLE dw.stg_aduana RENAME COLUMN "FLETE USD" TO flete_usd;
ALTER TABLE dw.stg_aduana RENAME COLUMN "SEGURO USD" TO seguro_usd;
ALTER TABLE dw.stg_aduana RENAME COLUMN "IMPONIBLE USD" TO imponible_usd;
ALTER TABLE dw.stg_aduana RENAME COLUMN "IMPONIBLE GS" TO imponible_gs;
ALTER TABLE dw.stg_aduana RENAME COLUMN "AJUSTE INCLUIR" TO ajuste_incluir;
ALTER TABLE dw.stg_aduana RENAME COLUMN "AJUSTE DEDUCIR" TO ajuste_deducir;
""")