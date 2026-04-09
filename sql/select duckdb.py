import duckdb
DB_PATH = r"C:/Información/proyectos/aduana_bi/db/aduana.duckdb"
con = duckdb.connect(DB_PATH)

queries = {
    'Tablas existentes': 'SHOW TABLES;',
    'Estructura dim_operacion': 'DESCRIBE dim_operacion;',
    'Primeros 10 registros dim_operacion': 'SELECT * FROM dim_operacion LIMIT 10;',
    'Conteo fact_aduana_item': 'SELECT COUNT(*) FROM fact_aduana_item;',
    'Integridad id_operacion': '''
        SELECT DISTINCT id_operacion FROM fact_aduana_item
        WHERE id_operacion NOT IN (SELECT id_operacion FROM dim_operacion);
    '''
}

for desc, query in queries.items():
    print(f"\n--- {desc} ---")
    result = con.execute(query).fetchall()
    for row in result:
        print(row)

con.close()