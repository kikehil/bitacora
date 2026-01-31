import pandas as pd
import sqlite3
import os
import random
import string

def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def load_usuarios_and_sync():
    db_paths = ['bitacora.db', 'instance/bitacora.db']
    excel_file = 'usuarios.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"Error: No se encuentra el archivo {excel_file}")
        return

    print(f"Leyendo {excel_file}...")
    df = pd.read_excel(excel_file)
    
    # Normalizar columnas
    df.columns = [str(col).strip().upper() for col in df.columns]
    print("Columnas encontradas:", df.columns.tolist())
    
    # Mapeo de columnas basado en ejecuciones previas
    col_nombre = 'NOMBRE'
    col_usuario = 'USUARIO'
    col_rol = 'ROL'
    col_pwd = 'CONTRASEÑA' if 'CONTRASEÑA' in df.columns else ('CONTRASEA' if 'CONTRASEA' in df.columns else None)

    usuarios_nuevos_pwd = []

    for path in db_paths:
        if not os.path.exists(path):
            continue
            
        print(f"--- Procesando usuarios en: {path} ---")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        count = 0
        for _, row in df.iterrows():
            nombre = str(row.get(col_nombre, '')).strip()
            usuario = str(row.get(col_usuario, '')).strip().lower()
            rol = str(row.get(col_rol, 'lider')).strip().lower()
            pwd = str(row.get(col_pwd, '')) if col_pwd else ''
            
            if not usuario or usuario == 'nan' or usuario == '':
                continue
            
            # Si no tiene password, generar una
            if not pwd or pwd == 'nan' or pwd == '':
                # Solo generar una vez por usuario para reportar al final
                pwd_existente = next((u['password'] for u in usuarios_nuevos_pwd if u['usuario'] == usuario), None)
                if not pwd_existente:
                    pwd = generate_password()
                    usuarios_nuevos_pwd.append({'usuario': usuario, 'nombre': nombre, 'password': pwd})
                else:
                    pwd = pwd_existente
            
            try:
                # Usar INSERT OR IGNORE o REPLACE. 
                # Si es Enrique Gil, no lo sobreescribimos para no perder su acceso admin actual
                if usuario == 'enrique.gil@oxxo.com':
                    continue

                cursor.execute("""
                    INSERT INTO usuarios (usuario, nombre, password, rol) 
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(usuario) DO UPDATE SET 
                        nombre=excluded.nombre, 
                        rol=excluded.rol,
                        password=CASE WHEN usuarios.password = '' THEN excluded.password ELSE usuarios.password END
                """, (usuario, nombre, pwd, rol))
                count += 1
            except Exception as e:
                print(f"Error procesando {usuario}: {e}")
        
        conn.commit()
        conn.close()
        print(f"Se procesaron {count} usuarios en {path}")

    # Mostrar reporte de contraseñas generadas
    if usuarios_nuevos_pwd:
        print("\n" + "="*50)
        print("REPORTE DE CONTRASEÑAS GENERADAS")
        print("="*50)
        for u in usuarios_nuevos_pwd:
            print(f"Nombre: {u['nombre']:<30} | Usuario: {u['usuario']:<30} | Password: {u['password']}")
        print("="*50)
    else:
        print("\nNo se generaron contraseñas nuevas.")

if __name__ == "__main__":
    load_usuarios_and_sync()

