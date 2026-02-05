import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'bitacora.db')

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    table = 'asesor_tienda'
    print(f"\nSchema for '{table}':")
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
        
    print(f"Sample row from '{table}':")
    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
    row = cursor.fetchone()
    print(row)

    conn.close()
except Exception as e:
    print(f"Error: {e}")
