
import sqlite3
import os
import sys

# 1. Verify app.py content
print("--- Checking app.py ---")
try:
    with open('app.py', 'r') as f:
        content = f.read()
        if "if role == 'ADMIN':" in content and "SELECT cr, name FROM stores" in content:
            print("SUCCESS: app.py contains the Admin logic fix.")
        else:
            print("FAILURE: app.py DOES NOT contain the Admin logic fix.")
            print("Snippet from file around 'get_stores':")
            # Find get_stores and print a few lines
            idx = content.find("def get_stores")
            if idx != -1:
                print(content[idx:idx+500])
except Exception as e:
    print(f"Error reading app.py: {e}")

# 2. Verify Database
print("\n--- Checking Database ---")
DB_PATH = 'bitacora.db'
if not os.path.exists(DB_PATH):
    print("FAILURE: bitacora.db not found.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count stores
        count = cursor.execute("SELECT COUNT(*) FROM stores").fetchone()[0]
        print(f"Total Stores in DB: {count}")
        
        # Check User
        email = 'enrique.gil@oxxo.com'
        user = cursor.execute("SELECT username, role FROM users WHERE username = ?", (email,)).fetchone()
        if user:
            print(f"User found: {user[0]}, Role: {user[1]}")
            
            # Simulate logic
            role = user[1]
            if role == 'ADMIN':
                stores = cursor.execute('SELECT cr, name FROM stores').fetchall()
                print(f"Simulated Logic for ADMIN: Found {len(stores)} stores.")
            else:
                stores = cursor.execute('SELECT cr, name FROM stores WHERE advisor_id = ?', (email,)).fetchall()
                print(f"Simulated Logic for ASESOR: Found {len(stores)} stores.")
        else:
            print(f"FAILURE: User {email} not found in DB.")
            # List all users to see what's there
            all_users = cursor.execute("SELECT username FROM users").fetchall()
            print(f"Available users: {[u[0] for u in all_users]}")

        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")
