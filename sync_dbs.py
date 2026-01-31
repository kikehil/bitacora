import sqlite3
import os

def final_sync():
    db_paths = ['bitacora.db', 'instance/bitacora.db']
    user_email = 'enrique.gil@oxxo.com'
    target_pass = 'Netbios85*'
    
    for path in db_paths:
        if os.path.exists(path):
            print(f"--- Sincronizando DB en: {path} ---")
            try:
                conn = sqlite3.connect(path)
                cursor = conn.cursor()
                
                # Limpiar y Recrear
                cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (user_email,))
                cursor.execute("""
                    INSERT INTO usuarios (usuario, nombre, password, rol) 
                    VALUES (?, ?, ?, ?)
                """, (user_email, 'Enrique Gil', target_pass, 'admin'))
                
                conn.commit()
                
                # Verificar
                cursor.execute("SELECT usuario FROM usuarios WHERE usuario = ?", (user_email,))
                if cursor.fetchone():
                    print(f"USUARIO CREADO EXITOSAMENTE EN {path}")
                
                conn.close()
            except Exception as e:
                print(f"Error en {path}: {e}")

if __name__ == "__main__":
    final_sync()

