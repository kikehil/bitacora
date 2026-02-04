import sqlite3
import sys

DB_PATH = "bitacora.db"

def main():
    if len(sys.argv) < 2:
        print("Uso: python tools/check_user.py <email>")
        return

    email = sys.argv[1].strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    row = cur.execute(
        "SELECT username, role, password, cr FROM users WHERE lower(username) = ?",
        (email,),
    ).fetchone()
    conn.close()

    if not row:
        print("NO_EXISTE")
        return

    print(f"USUARIO: {row[0]}")
    print(f"ROL: {row[1]}")
    print(f"PASSWORD: {row[2]}")
    print(f"CR: {row[3]}")

if __name__ == "__main__":
    main()





