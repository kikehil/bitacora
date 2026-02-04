import sqlite3
import os

def update_roles_and_users():
    db_paths = ['bitacora.db', 'instance/bitacora.db']
    
    for path in db_paths:
        if not os.path.exists(path):
            continue
            
        print(f"--- Actualizando roles en: {path} ---")
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # 1. Cambiar 'colaborador' a 'lider' (Nuevo rol solicitado)
        cursor.execute("UPDATE usuarios SET rol = 'lider' WHERE rol = 'colaborador'")
        
        # 2. Asegurar que Enrique Gil sea Admin
        cursor.execute("UPDATE usuarios SET rol = 'admin' WHERE usuario = 'enrique.gil@oxxo.com'")
        
        # 3. Verificar roles actuales
        cursor.execute("SELECT rol, COUNT(*) FROM usuarios GROUP BY rol")
        print("Conteo de usuarios por rol:", cursor.fetchall())
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    update_roles_and_users()

