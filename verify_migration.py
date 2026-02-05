import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'bitacora.db')

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Verifying Users...")
    users_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"Users count: {users_count}")
    
    if users_count > 0:
        print("Sample User:")
        user = cursor.execute("SELECT username, name, role, cr FROM users LIMIT 1").fetchone()
        print(user)
        
    print("\nVerifying Stores...")
    stores_count = cursor.execute("SELECT COUNT(*) FROM stores").fetchone()[0]
    print(f"Stores count: {stores_count}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
