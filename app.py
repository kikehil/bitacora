import sqlite3
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

DB_PATH = 'bitacora.db'

def migrate_users_table(conn):
    cursor = conn.cursor()
    # Detectar esquema actual
    table_info = cursor.execute("PRAGMA table_info(users)").fetchall()
    columns = [row[1] for row in table_info]
    table_sql_row = cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='users'"
    ).fetchone()
    table_sql = table_sql_row[0] if table_sql_row else ""

    has_role_check = "CHECK(role" in (table_sql or "")
    has_cr_column = "cr" in columns

    if has_role_check or not has_cr_column:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                name TEXT NOT NULL,
                cr TEXT
            )
        ''')
        # Copiar datos existentes
        if columns:
            copy_cols = [c for c in columns if c in ["id", "username", "password", "role", "name", "cr"]]
            cols_str = ",".join(copy_cols)
            cursor.execute(f"INSERT INTO users_new ({cols_str}) SELECT {cols_str} FROM users")
        cursor.execute("DROP TABLE users")
        cursor.execute("ALTER TABLE users_new RENAME TO users")
        conn.commit()

def migrate_withdrawals_table(conn):
    cursor = conn.cursor()
    table_info = cursor.execute("PRAGMA table_info(withdrawals)").fetchall()
    columns = [row[1] for row in table_info]
    table_sql_row = cursor.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='withdrawals'"
    ).fetchone()
    table_sql = table_sql_row[0] if table_sql_row else ""

    needs_migration = False
    required_cols = ["store_name", "retiro_num", "caja"]
    for col in required_cols:
        if col not in columns:
            needs_migration = True

    if needs_migration:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS withdrawals_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cr TEXT NOT NULL,
                store_name TEXT,
                amount REAL NOT NULL,
                retiro_num TEXT NOT NULL,
                caja TEXT NOT NULL DEFAULT '',
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                collaborator1 TEXT NOT NULL,
                collaborator2 TEXT,
                photo_url TEXT
            )
        ''')
        if columns:
            copy_cols = [c for c in columns if c in [
                "id", "cr", "store_name", "amount", "retiro_num", "caja",
                "date", "time", "collaborator1", "collaborator2", "photo_url"
            ]]
            if copy_cols:
                cols_str = ",".join(copy_cols)
                if "caja" in copy_cols:
                    cursor.execute(
                        f"INSERT INTO withdrawals_new ({cols_str}) "
                        f"SELECT {cols_str} FROM withdrawals"
                    )
                else:
                    # Migración segura: rellenar caja con valor vacío
                    cursor.execute(
                        f"INSERT INTO withdrawals_new ({cols_str}, caja) "
                        f"SELECT {cols_str}, '' FROM withdrawals"
                    )
        cursor.execute("DROP TABLE withdrawals")
        cursor.execute("ALTER TABLE withdrawals_new RENAME TO withdrawals")
        conn.commit()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    migrate_users_table(conn)
    migrate_withdrawals_table(conn)
    migrate_users_table(conn)
    # Tabla de usuarios (si no existe)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            cr TEXT
        )
    ''')
    # Tabla de retiros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cr TEXT NOT NULL,
            store_name TEXT,
            amount REAL NOT NULL,
            retiro_num TEXT NOT NULL,
            caja TEXT NOT NULL DEFAULT '',
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            collaborator1 TEXT NOT NULL,
            collaborator2 TEXT,
            photo_url TEXT
        )
    ''')
    # Tabla de tiendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stores (
            cr TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            advisor_id TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return send_from_directory('.', 'bitacora.html')

@app.route('/logo.svg')
def logo():
    return send_from_directory('.', 'logo.svg')

@app.route('/uploads/<path:filename>')
def uploads(filename):
    return send_from_directory('uploads', filename)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    user = cursor.execute(
        'SELECT username, name, role, cr FROM users WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    conn.close()
    
    if user:
        return jsonify({"success": True, "user": dict(user)})
    else:
        return jsonify({"success": False, "message": "Credenciales incorrectas"}), 401

@app.route('/api/advisor/stats/<email>', methods=['GET'])
def get_stats(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Conteo de tiendas
    stores_count = cursor.execute('SELECT COUNT(*) FROM stores WHERE advisor_id = ?', (email,)).fetchone()[0]
    
    # Suma de hoy
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    today_amount = cursor.execute('''
        SELECT SUM(w.amount) 
        FROM withdrawals w
        JOIN stores s ON w.cr = s.cr
        WHERE s.advisor_id = ? AND w.date = ?
    ''', (email, today)).fetchone()[0] or 0
    
    conn.close()
    return jsonify({
        "total_stores": stores_count,
        "today_amount": today_amount
    })

@app.route('/api/advisor/stores/<email>', methods=['GET'])
def get_stores(email):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    stores = cursor.execute('SELECT cr, name FROM stores WHERE advisor_id = ?', (email,)).fetchall()
    conn.close()
    return jsonify([dict(s) for s in stores])

@app.route('/api/withdrawals', methods=['GET'])
def list_withdrawals():
    requester_role = request.args.get('requester_role')
    requester_email = request.args.get('requester_email')
    date = request.args.get('date')
    employee = request.args.get('employee')

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if requester_role != 'LIDER':
            conn.close()
            return jsonify({"success": False, "message": "No autorizado"}), 403

        leader = cursor.execute(
            'SELECT cr FROM users WHERE username = ? AND role = ?',
            (requester_email, 'LIDER')
        ).fetchone()
        if not leader or not leader['cr']:
            conn.close()
            return jsonify([])

        params = [leader['cr']]
        query = '''
            SELECT id, cr, store_name, amount, retiro_num, caja, date, time, collaborator1, photo_url
            FROM withdrawals
            WHERE cr = ?
        '''
        if date:
            query += ' AND date = ?'
            params.append(date)
        if employee:
            query += ' AND collaborator1 = ?'
            params.append(employee)
        query += ' ORDER BY date DESC, time DESC'

        rows = cursor.execute(query, params).fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/withdrawals/report', methods=['GET'])
def report_withdrawals():
    requester_role = (request.args.get('requester_role') or '').upper()
    requester_email = request.args.get('requester_email')
    date = request.args.get('date')
    employee = request.args.get('employee')
    advisor = request.args.get('advisor')
    store_query = (request.args.get('store') or '').strip()

    if requester_role not in ['ADMIN', 'ASESOR']:
        return jsonify({"success": False, "message": "No autorizado"}), 403

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        params = []
        query = '''
            SELECT w.id, w.cr, w.store_name, w.amount, w.retiro_num, w.caja,
                   w.date, w.time, w.collaborator1, w.photo_url, s.advisor_id
            FROM withdrawals w
            LEFT JOIN stores s ON w.cr = s.cr
            WHERE 1=1
        '''
        if requester_role == 'ASESOR':
            query += ' AND s.advisor_id = ?'
            params.append(requester_email)
        if date:
            query += ' AND w.date = ?'
            params.append(date)
        if employee:
            query += ' AND w.collaborator1 = ?'
            params.append(employee)
        if store_query:
            query += ' AND (w.cr LIKE ? OR w.store_name LIKE ?)'
            like = f"%{store_query}%"
            params.extend([like, like])
        if requester_role == 'ADMIN' and advisor:
            query += ' AND s.advisor_id = ?'
            params.append(advisor)

        query += ' ORDER BY w.date DESC, w.time DESC'

        rows = cursor.execute(query, params).fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/withdrawals/self', methods=['GET'])
def list_own_withdrawals():
    requester_role = (request.args.get('requester_role') or '').upper()
    requester_email = request.args.get('requester_email')

    if requester_role not in ['ENCARGADO', 'CAJERO', 'AYUDANTE']:
        return jsonify({"success": False, "message": "No autorizado"}), 403

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        user_row = cursor.execute(
            'SELECT cr FROM users WHERE username = ? AND role = ?',
            (requester_email, requester_role)
        ).fetchone()
        if not user_row:
            conn.close()
            return jsonify([])

        rows = cursor.execute(
            '''SELECT id, cr, store_name, amount, retiro_num, caja, date, time, photo_url
               FROM withdrawals
               WHERE collaborator1 = ?
               ORDER BY date DESC, time DESC''',
            (requester_email,)
        ).fetchall()
        conn.close()
        return jsonify([dict(r) for r in rows])
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/withdrawals', methods=['POST'])
def create_withdrawal():
    cr = request.form.get('cr')
    amount = request.form.get('amount')
    retiro_num = request.form.get('retiro_num')
    caja = request.form.get('caja')
    collaborator1 = request.form.get('collaborator1')
    role = (request.form.get('role') or '').upper()
    photo = request.files.get('photo')

    if role not in ['LIDER', 'ENCARGADO', 'CAJERO', 'AYUDANTE', 'ADMIN']:
        return jsonify({"success": False, "message": "Rol no autorizado para registrar retiros"}), 403

    if not cr or not amount or not retiro_num or not caja or not collaborator1 or not photo:
        return jsonify({"success": False, "message": "Faltan datos obligatorios o la foto es requerida"}), 400

    try:
        from datetime import datetime
        now = datetime.now()
        date = now.strftime('%Y-%m-%d')
        time = now.strftime('%H:%M')

        # Validar tipo de archivo
        allowed_ext = {'.png', '.jpg', '.jpeg'}
        _, ext = os.path.splitext(photo.filename.lower())
        if ext not in allowed_ext:
            return jsonify({"success": False, "message": "Formato inválido. Solo PNG o JPEG/JPG."}), 400

        # Guardar foto
        upload_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"{cr}_{date.replace('-', '')}_{time.replace(':', '')}{ext}"
        file_path = os.path.join(upload_dir, filename)
        photo.save(file_path)
        photo_url = f"/uploads/{filename}"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        store_name_row = cursor.execute('SELECT name FROM stores WHERE cr = ?', (cr,)).fetchone()
        store_name = store_name_row[0] if store_name_row else ''

        cursor.execute(
            '''INSERT INTO withdrawals (cr, store_name, amount, retiro_num, caja, date, time, collaborator1, collaborator2, photo_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (cr, store_name, float(amount), retiro_num, caja, date, time, collaborator1, None, photo_url)
        )
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Retiro registrado correctamente"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/store-info/<cr>', methods=['GET'])
def get_store_info(cr):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    store = cursor.execute('SELECT cr, name, advisor_id FROM stores WHERE cr = ?', (cr,)).fetchone()
    if not store:
        conn.close()
        return jsonify({"success": False, "message": "Tienda no encontrada"}), 404
    advisor = cursor.execute(
        'SELECT name, username FROM users WHERE username = ?',
        (store['advisor_id'],)
    ).fetchone()
    conn.close()
    return jsonify({
        "cr": store['cr'],
        "store_name": store['name'],
        "advisor_name": advisor['name'] if advisor else store['advisor_id'],
        "advisor_email": advisor['username'] if advisor else store['advisor_id']
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    requester_role = request.args.get('requester_role')
    requester_email = request.args.get('requester_email')

    print('--- DEBUG GESTIÓN USUARIOS (Flask) ---')
    print('Solicitante:', requester_email)
    print('Rol:', requester_role)

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if requester_role == 'ADMIN':
            users = cursor.execute('SELECT id, username, name, role, cr FROM users').fetchall()
        elif requester_role == 'ASESOR':
            stores = cursor.execute('SELECT cr FROM stores WHERE advisor_id = ?', (requester_email,)).fetchall()
            cr_list = [s['cr'] for s in stores]
            print('CRs supervisados:', cr_list)

            if len(cr_list) == 0:
                conn.close()
                return jsonify([])

            placeholders = ','.join(['?'] * len(cr_list))
            users = cursor.execute(
                f'''SELECT id, username, name, role, cr 
                    FROM users 
                    WHERE cr IN ({placeholders})
                    AND role NOT IN ('ADMIN', 'ASESOR')''',
                cr_list
            ).fetchall()
        elif requester_role == 'LIDER':
            leader = cursor.execute(
                'SELECT cr FROM users WHERE username = ? AND role = ?',
                (requester_email, 'LIDER')
            ).fetchone()
            if not leader or not leader['cr']:
                conn.close()
                return jsonify([])

            users = cursor.execute(
                '''SELECT id, username, name, role, cr 
                   FROM users 
                   WHERE cr = ?
                   AND role IN ('ENCARGADO', 'CAJERO', 'AYUDANTE')''',
                (leader['cr'],)
            ).fetchall()
        else:
            conn.close()
            return jsonify({"success": False, "message": "No autorizado"}), 403

        conn.close()
        return jsonify([dict(u) for u in users] if users else [])
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.json
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        requester_role = data.get('requester_role')
        requester_email = data.get('requester_email')
        role = (data.get('role') or '').upper()
        cr = data.get('cr')

        if requester_role == 'ASESOR':
            if role in ['ADMIN', 'ASESOR']:
                conn.close()
                return jsonify({"success": False, "message": "No autorizado para asignar ese rol"}), 403

            store = cursor.execute(
                'SELECT cr FROM stores WHERE cr = ? AND advisor_id = ?',
                (cr, requester_email)
            ).fetchone()
            if not store:
                conn.close()
                return jsonify({"success": False, "message": "CR no autorizado"}), 403
        elif requester_role == 'LIDER':
            if role not in ['ENCARGADO', 'CAJERO', 'AYUDANTE']:
                conn.close()
                return jsonify({"success": False, "message": "Rol no permitido para líder"}), 403
            leader = cursor.execute(
                'SELECT cr FROM users WHERE username = ? AND role = ?',
                (requester_email, 'LIDER')
            ).fetchone()
            if not leader or not leader['cr'] or leader['cr'] != cr:
                conn.close()
                return jsonify({"success": False, "message": "CR no autorizado"}), 403

        cursor.execute(
            'INSERT INTO users (username, password, name, role, cr) VALUES (?, ?, ?, ?, ?)',
            (data['username'], data['password'], data['name'], role, cr)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Usuario creado"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/users/change-password', methods=['PATCH'])
def change_password():
    data = request.json or {}
    username = data.get('username')
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')

    if not username or not current_password or not new_password:
        return jsonify({"success": False, "message": "Faltan datos obligatorios"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        user = cursor.execute(
            'SELECT id FROM users WHERE username = ? AND password = ?',
            (username, current_password)
        ).fetchone()
        if not user:
            conn.close()
            return jsonify({"success": False, "message": "Contraseña actual incorrecta"}), 400

        cursor.execute(
            'UPDATE users SET password = ? WHERE username = ?',
            (new_password, username)
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Contraseña actualizada"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/users/reset-password', methods=['PATCH'])
def reset_password():
    data = request.json
    username = data.get('username')
    new_password = data.get('newPassword')

    if not username or not new_password:
        return jsonify({"success": False, "message": "Faltan datos"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE users SET password = ? WHERE username = ?',
            (new_password, username)
        )
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"success": False, "message": "Usuario no encontrado"}), 404

        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Contraseña actualizada"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
