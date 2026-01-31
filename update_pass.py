import sqlite3

def update_user_password():
    try:
        conn = sqlite3.connect('instance/bitacora.db') # Flask-SQLAlchemy suele ponerlo en instance/
    except:
        conn = sqlite3.connect('bitacora.db')
        
    cursor = conn.cursor()
    
    # Verificar si el usuario existe
    cursor.execute("SELECT usuario FROM usuarios WHERE usuario='enrique.gil@oxxo.com'")
    user = cursor.fetchone()
    
    if user:
        cursor.execute("UPDATE usuarios SET password='Netbios85*' WHERE usuario='enrique.gil@oxxo.com'")
        conn.commit()
        print("Contraseña actualizada exitosamente para enrique.gil@oxxo.com")
    else:
        print("El usuario enrique.gil@oxxo.com no fue encontrado en la base de datos.")
    
    conn.close()

if __name__ == "__main__":
    update_user_password()

