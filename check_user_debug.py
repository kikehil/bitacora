import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'bitacora.db')

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Search for enrique (case insensitive like search)
    print("Searching for 'enrique'...")
    cursor.execute("SELECT username, password, role FROM users WHERE username LIKE '%enrique%'")
    users = cursor.fetchall()
    
    if users:
        for u in users:
            print(f"User found: Username='{u[0]}', Password='{u[1]}', Role='{u[2]}'")
    else:
        print("No user found matching 'enrique'")

    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
