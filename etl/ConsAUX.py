import duckdb
import pandas as pd
DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"




con = duckdb.connect(r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb")
print(con.execute("PRAGMA table_info('dw.stg_aduana');").fetchdf())


con = duckdb.connect(r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb")
con.execute("DROP TABLE dw.stg_destinaciones;")
con.execute("DROP TABLE dw.stg_aduana")
print(con.execute("PRAGMA table_info('dw.stg_aduana');").fetchdf())
print(con.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema='dw';").fetchdf())
