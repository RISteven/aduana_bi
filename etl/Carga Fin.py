import pandas as pd
import duckdb
import numpy as np
from tqdm import tqdm
import os

# Definir rutas

bronze_path = './data_lake/bronze/DatosCSV.csv' 
silver_path = './data_lake/silver/' 
duckdb_path = './aduana.duckdb'

# Validar existencia del archivo CSV

if not os.path.exists(bronze_path):
    raise FileNotFoundError(f"Archivo no encontrado: {bronze_path} . Verifica la ruta y el nombre del archivo.")
if not os.path.exists(silver_path):
    raise FileNotFoundError(f"Archivo no encontrado: {silver_path} . Verifica la ruta y el nombre del archivo.")

if not os.path.exists(bronze_path):
    raise FileNotFoundError(f"Archivo no encontrado: {duckdb_path} . Verifica la ruta y el nombre del archivo.")

# Leer datos Bronze


print('Leyendo datos Bronze...')

# Intentar detectar la codificación para evitar errores

try: 
    import chardet 
    with open(bronze_path, 'rb') as f: 
        rawdata = f.read() 
    result = chardet.detect(rawdata) 
    encoding = result['encoding'] 
    engine='python'
    print(f"Codificación detectada: {encoding}") 
except ImportError: encoding = 'latin1'  

# Valor por defecto si no se tiene chardet
# Leer CSV con la codificación detectada

try: 
    df_bronze = pd.read_csv(bronze_path, sep=';', encoding=encoding, engine='python') 
except Exception as e:
    print(f"Error al leer el archivo CSV: {e}")
raise

# Limpieza y normalización básica

print('Limpiando y normalizando datos...') 
df_bronze.columns = df_bronze.columns.str.strip().str.lower() 
df_bronze['fecha'] = pd.to_datetime(df_bronze['fecha'], dayfirst=True, errors='coerce')
df_bronze = df_bronze.dropna(subset=['fecha'])

# Crear conexión DuckDB

con = duckdb.connect(database=duckdb_path, read_only=False)

# Crear tablas dimensiones

print('Construyendo dimensiones...')

# Dim_Operacion

dim_operacion = df_bronze[['id_operacion', 'descripcion_operacion']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_operacion') 
con.register('dim_operacion_df', dim_operacion) 
con.execute('CREATE TABLE dim_operacion AS SELECT * FROM dim_operacion_df')

# Dim_Destinacion

dim_destinacion = df_bronze[['codigo_destinacion', 'descripcion_destinacion']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_destinacion') 
con.register('dim_destinacion_df', dim_destinacion) 
con.execute('CREATE TABLE dim_destinacion AS SELECT * FROM dim_destinacion_df')

# Dim_Regimen

dim_regimen = df_bronze[['codigo_regimen', 'descripcion_regimen']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_regimen') 
con.register('dim_regimen_df', dim_regimen)
con.execute('CREATE TABLE dim_regimen AS SELECT * FROM dim_regimen_df')

# Dim_Pais

dim_pais = df_bronze[['codigo_pais', 'descripcion_pais']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_pais') 
con.register('dim_pais_df', dim_pais) 
con.execute('CREATE TABLE dim_pais AS SELECT * FROM dim_pais_df')

# Dim_Aduana

dim_aduana = df_bronze[['codigo_aduana', 'descripcion_aduana']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_aduana') 
con.register('dim_aduana_df', dim_aduana) 
con.execute('CREATE TABLE dim_aduana AS SELECT * FROM dim_aduana_df')

# Dim_Producto

dim_producto = df_bronze[['ncm', 'descripcion_producto']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_producto') 
con.register('dim_producto_df', dim_producto) 
con.execute('CREATE TABLE dim_producto AS SELECT * FROM dim_producto_df')

# Dim_MedioTransporte

dim_medio_transporte = df_bronze[['codigo_medio_transporte', 'descripcion_medio_transporte']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_medio_transporte') 
con.register('dim_medio_transporte_df', dim_medio_transporte) 
con.execute('CREATE TABLE dim_medio_transporte AS SELECT * FROM dim_medio_transporte_df')

# Dim_Canal

dim_canal = df_bronze[['codigo_canal', 'descripcion_canal']].drop_duplicates().reset_index(drop=True)
con.execute('DROP TABLE IF EXISTS dim_canal')
con.register('dim_canal_df', dim_canal) 
con.execute('CREATE TABLE dim_canal AS SELECT * FROM dim_canal_df')

# Dim_UnidadMedida

dim_unidad_medida = df_bronze[['codigo_unidad_medida', 'descripcion_unidad_medida']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_unidad_medida')
con.register('dim_unidad_medida_df', dim_unidad_medida) 
con.execute('CREATE TABLE dim_unidad_medida AS SELECT * FROM dim_unidad_medida_df')

# Dim_Acuerdo

if 'codigo_acuerdo' in df_bronze.columns and 'descripcion_acuerdo' in df_bronze.columns: dim_acuerdo = df_bronze[['codigo_acuerdo', 'descripcion_acuerdo']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_acuerdo') 
con.register('dim_acuerdo_df', dim_acuerdo)
con.execute('CREATE TABLE dim_acuerdo AS SELECT * FROM dim_acuerdo_df')

# Dim_Marca

if 'codigo_marca' in df_bronze.columns and 'descripcion_marca' in df_bronze.columns: dim_marca = df_bronze[['codigo_marca', 'descripcion_marca']].drop_duplicates().reset_index(drop=True) 
con.execute('DROP TABLE IF EXISTS dim_marca')
con.register('dim_marca_df', dim_marca) 
con.execute('CREATE TABLE dim_marca AS SELECT * FROM dim_marca_df')

# Dim_Fecha

print('Construyendo Dim_Fecha...') 
fechas = pd.DataFrame({'fecha': pd.date_range(start=df_bronze['fecha'].min(), end=df_bronze['fecha'].max())}) 
fechas['anio'] = fechas['fecha'].dt.year 
fechas['mes'] = fechas['fecha'].dt.month 
fechas['dia'] = fechas['fecha'].dt.day 
fechas['trimestre'] = fechas['fecha'].dt.quarter 
con.execute('DROP TABLE IF EXISTS dim_fecha') 
con.register('dim_fecha_df', fechas) 
con.execute('CREATE TABLE dim_fecha AS SELECT * FROM dim_fecha_df')

# Construcción tabla de hechos

print('Construyendo tabla de hechos fact_aduana_item...')

# Selección y renombrado de columnas clave y medidas

fact_cols = [ 'id_operacion', 'codigo_destinacion', 'codigo_regimen', 'codigo_pais', 'codigo_aduana', 'ncm', 'codigo_medio_transporte', 'codigo_canal', 'codigo_unidad_medida', 'codigo_acuerdo', 'codigo_marca', 'fecha', 'cantidad', 'valor_fob', 'valor_cif' ]
fact_aduana_item = df_bronze[fact_cols].copy()

# Insertar en DuckDB

con.execute('DROP TABLE IF EXISTS fact_aduana_item') 
con.register('fact_aduana_item_df', fact_aduana_item) 
con.execute('CREATE TABLE fact_aduana_item AS SELECT * FROM fact_aduana_item_df')
print('Carga ETL completada con éxito.')

# Cerrar conexión
con.close()