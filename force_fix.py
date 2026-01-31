import sqlite3

def fix_and_verify():
    conn = sqlite3.connect('bitacora.db')
    cursor = conn.cursor()
    
    # 1. Asegurar que el usuario existe con los datos exactos
    user_email = 'enrique.gil@oxxo.com'
    target_pass = 'Netbios85*'
    
    print(f"--- Corrigiendo usuario: {user_email} ---")
    
    # Eliminar si existe para evitar conflictos y recrear limpio
    cursor.execute("DELETE FROM usuarios WHERE usuario = ?", (user_email,))
    
    # Insertar de nuevo con rol admin
    cursor.execute("""
        INSERT INTO usuarios (usuario, nombre, password, rol) 
        VALUES (?, ?, ?, ?)
    """, (user_email, 'Enrique Gil', target_pass, 'admin'))
    
    conn.commit()
    
    # 2. Verificar lo que quedó en la base de datos
    cursor.execute("SELECT usuario, password, rol FROM usuarios WHERE usuario = ?", (user_email,))
    row = cursor.fetchone()
    
    if row:
        print(f"CONFIRMADO EN DB:")
        print(f"Usuario: '{row[0]}'")
        print(f"Password: '{row[1]}'")
        print(f"Rol: '{row[2]}'")
    else:
        print("ERROR: No se pudo crear el usuario.")
        
    conn.close()

if __name__ == "__main__":
    fix_and_verify()

