import os
import duckdb
import re
import pandas as pd

BASE = r"C:\Información\proyectos\aduana_bi"

os.system(f'python "{BASE}\\sql\\CrearTablas.py"')
os.system(f'python "{BASE}\\etl\\ETL-Cargar-Staging.py"')
os.system(f'python "{BASE}\\etl\\03_cargar_dimensiones.py"')
os.system(f'python "{BASE}\\etl\\04_cargar_fact.py"')
os.system(f'python "{BASE}\\etl\\ConsAUX.py"')