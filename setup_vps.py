import sqlite3
import os
import sys

# Add current directory to path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import init_db, DB_PATH

def setup():
    print(f"Using Database at: {DB_PATH}")
    print("Initializing Database Structure...")
    try:
        init_db()
        print("Database structure initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if any user exists
    try:
        cursor.execute("SELECT count(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Database already contains {count} users.")
            # Verify if admin exists
            cursor.execute("SELECT username FROM users WHERE role='ADMIN'")
            admins = cursor.fetchall()
            if admins:
                print("Admin users found:", [a[0] for a in admins])
            else:
                print("WARNING: No ADMIN user found.")
        else:
            print("Database is empty. Creating default admin user...")
            # username, password, role, name, cr
            cursor.execute("INSERT INTO users (username, password, role, name, cr) VALUES (?, ?, ?, ?, ?)",
                           ('admin@oxxo.com', 'admin123', 'ADMIN', 'Administrador', ''))
            conn.commit()
            print("✔ Default Admin created successfully.")
            print("-------------------------------------")
            print("User: admin@oxxo.com")
            print("Pass: admin123")
            print("-------------------------------------")
            
    except Exception as e:
        print(f"Error checking/creating users: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    setup()
