# import duckdb
# import pandas as pd
# DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"




# con = duckdb.connect(r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb")
# print(con.execute("PRAGMA table_info('dw.stg_aduana');").fetchdf())


# con = duckdb.connect(r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb")
# con.execute("DROP TABLE dw.stg_destinaciones;")
# con.execute("DROP TABLE dw.stg_aduana")
# print(con.execute("PRAGMA table_info('dw.stg_aduana');").fetchdf())
# print(con.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema='dw';").fetchdf())


import duckdb

con = duckdb.connect("C:/duckdb/aduana.duckdb")

tablas = [
    "dim_acuerdo",
    "dim_aduana",
    "dim_canal",
    "dim_destinacion",
    "dim_fecha",
    "dim_marca",
    "dim_medio_transporte",
    "dim_operacion",
    "dim_pais",
    "dim_producto",
    "dim_regimen",
    "dim_unidad_medida",
    "fact_aduana_item"
]

for t in tablas:
    con.execute(f"COPY dw.{t} TO 'C:/duckdb/export/{t}.parquet' (FORMAT PARQUET);")

con.close()