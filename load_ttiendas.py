import pandas as pd
import sqlite3
import os

def load_ttiendas():
    db_paths = ['bitacora.db', 'instance/bitacora.db']
    excel_file = 'TTIENDAS.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"Error: No se encuentra el archivo {excel_file}")
        return

    print(f"Leyendo {excel_file}...")
    df = pd.read_excel(excel_file)
    
    # Normalizar columnas
    df.columns = [str(col).strip().upper() for col in df.columns]
    print("Columnas encontradas:", df.columns.tolist())
    
    # Mapeo de columnas (ajustar según el excel real)
    col_cr = 'CR TIENDA' if 'CR TIENDA' in df.columns else df.columns[0]
    col_nombre = 'NOMBRE TIENDA' if 'NOMBRE TIENDA' in df.columns else df.columns[1]
    col_distrito = 'DISTRITO' if 'DISTRITO' in df.columns else None

    for path in db_paths:
        if not os.path.exists(path):
            continue
            
        print(f"--- Llenando tiendas en: {path} ---")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            cr = str(row.get(col_cr, '')).strip()
            nombre = str(row.get(col_nombre, '')).strip()
            distrito = str(row.get(col_distrito, '')) if col_distrito else ''
            
            if not cr or cr == 'nan': continue
            
            try:
                cursor.execute("INSERT OR REPLACE INTO tiendas (cr, nombre, distrito) VALUES (?, ?, ?)",
                             (cr, nombre, distrito))
                count += 1
            except Exception as e:
                print(f"Error insertando {cr}: {e}")
        
        conn.commit()
        conn.close()
        print(f"Se cargaron {count} tiendas en {path}")

if __name__ == "__main__":
    load_ttiendas()

