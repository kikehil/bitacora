import sqlite3

def update_user_password():
    conn = sqlite3.connect('bitacora.db')
    cursor = conn.cursor()
    
    # Actualizar contraseña
    cursor.execute("UPDATE usuarios SET password='Netbios85*' WHERE usuario='enrique.gil@oxxo.com'")
    
    if cursor.rowcount > 0:
        conn.commit()
        print("Contraseña actualizada exitosamente para enrique.gil@oxxo.com")
    else:
        print("No se encontró al usuario enrique.gil@oxxo.com")
    
    conn.close()

if __name__ == "__main__":
    update_user_password()

