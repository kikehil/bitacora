import sqlite3

def check_and_fix():
    conn = sqlite3.connect('bitacora.db')
    cursor = conn.cursor()
    
    print("--- Verificando usuario ---")
    cursor.execute("SELECT usuario, password, rol FROM usuarios WHERE usuario = 'enrique.gil@oxxo.com'")
    user = cursor.fetchone()
    
    if user:
        print(f"Usuario encontrado: {user[0]}")
        print(f"Password actual: {user[1]}")
        print(f"Rol: {user[2]}")
        
        if user[1] != 'Netbios85*':
            print("Actualizando password a 'Netbios85*'...")
            cursor.execute("UPDATE usuarios SET password='Netbios85*' WHERE usuario='enrique.gil@oxxo.com'")
            conn.commit()
            print("Password actualizado.")
    else:
        print("Usuario 'enrique.gil@oxxo.com' NO existe. Creándolo...")
        cursor.execute("INSERT INTO usuarios (usuario, nombre, password, rol) VALUES ('enrique.gil@oxxo.com', 'Enrique Gil', 'Netbios85*', 'admin')")
        conn.commit()
        print("Usuario creado como admin.")
        
    conn.close()

if __name__ == "__main__":
    check_and_fix()

