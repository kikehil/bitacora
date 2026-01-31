import pandas as pd
import sqlite3
import random
import string
import os

def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def process_data():
    db_path = 'bitacora.db'
    
    # Conectar a SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Crear tabla usuarios
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        nombre TEXT,
        password TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    ''')

    # 2. Crear tabla tiendas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tiendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cr TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        distrito TEXT
    )
    ''')

    # 3. Crear tabla relacion asesor_tienda
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asesor_tienda (
        usuario_id INTEGER,
        tienda_id INTEGER,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY(tienda_id) REFERENCES tiendas(id),
        PRIMARY KEY(usuario_id, tienda_id)
    )
    ''')

    # 4. Crear tabla retiros (basado en el formulario)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS retiros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_retiro TEXT NOT NULL,
        tienda_cr TEXT NOT NULL,
        monto REAL NOT NULL,
        notas TEXT,
        imagen_fajilla TEXT,
        usuario_registro TEXT NOT NULL,
        usuario_confirma TEXT NOT NULL,
        fecha TEXT NOT NULL,
        hora TEXT NOT NULL,
        fecha_hora_registro TEXT NOT NULL
    )
    ''')

    # Cargar Usuarios
    print("Procesando usuarios...")
    df_usuarios = pd.read_excel('usuarios.xlsx')
    
    # Normalizar nombres de columnas a minúsculas y quitar espacios
    df_usuarios.columns = [str(col).strip().lower() for col in df_usuarios.columns]
    print("Columnas usuarios normalizadas:", df_usuarios.columns.tolist())
    
    # Mapeo de columnas basado en lo observado
    # 'nombre', 'usuario', 'rol', 'contraseña' (o similar)
    col_user = 'usuario'
    col_nombre = 'nombre'
    col_rol = 'rol'
    col_pwd = 'contraseña' if 'contraseña' in df_usuarios.columns else 'contrasea'
    
    usuarios_generados = []
    
    for _, row in df_usuarios.iterrows():
        user = str(row.get(col_user, '')).strip()
        nombre = str(row.get(col_nombre, '')).strip()
        pwd = str(row.get(col_pwd, '')).strip()
        rol = str(row.get(col_rol, 'colaborador')).strip()
        
        if not user or user == 'nan' or user == '':
            continue # Saltar filas sin usuario
            
        if not pwd or pwd == 'nan' or pwd == '':
            pwd = generate_password()
            usuarios_generados.append({'usuario': user, 'password': pwd})
        
        try:
            cursor.execute('INSERT INTO usuarios (usuario, nombre, password, rol) VALUES (?, ?, ?, ?)',
                         (user, nombre, pwd, rol))
        except sqlite3.IntegrityError:
            # Si ya existe, actualizar por si acaso
            cursor.execute('UPDATE usuarios SET nombre=?, password=?, rol=? WHERE usuario=?',
                         (nombre, pwd, rol, user))

    # Cargar Tiendas y Relación Asesor
    print("Procesando tiendas...")
    df_tiendas = pd.read_excel('TIENDAS.xlsx')
    
    # Normalizar nombres de columnas
    df_tiendas.columns = [str(col).strip().lower() for col in df_tiendas.columns]
    print("Columnas tiendas normalizadas:", df_tiendas.columns.tolist())
    
    # Mapeo: 'cr tienda', 'nombre tienda', 'asesor'
    col_cr = 'cr tienda'
    col_nombre_t = 'nombre tienda'
    col_asesor = 'asesor'
    
    for _, row in df_tiendas.iterrows():
        cr = str(row.get(col_cr, '')).strip()
        nombre_tienda = str(row.get(col_nombre_t, '')).strip()
        asesor_user = str(row.get(col_asesor, '')).strip()
        
        if not cr or cr == 'nan' or cr == '': continue
        
        # Insertar tienda
        try:
            cursor.execute('INSERT INTO tiendas (cr, nombre) VALUES (?, ?)',
                         (cr, nombre_tienda))
            tienda_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute('SELECT id FROM tiendas WHERE cr = ?', (cr,))
            tienda_id = cursor.fetchone()[0]
            
        # Relacionar con asesor si existe
        if asesor_user and asesor_user != 'nan' and asesor_user != '':
            cursor.execute('SELECT id FROM usuarios WHERE usuario = ?', (asesor_user,))
            user_res = cursor.fetchone()
            if user_res:
                user_id = user_res[0]
                try:
                    cursor.execute('INSERT INTO asesor_tienda (usuario_id, tienda_id) VALUES (?, ?)',
                                 (user_id, tienda_id))
                except sqlite3.IntegrityError:
                    pass

    conn.commit()
    conn.close()
    
    if usuarios_generados:
        print("\n--- USUARIOS CON CONTRASEÑAS GENERADAS ---")
        for u in usuarios_generados:
            print(f"Usuario: {u['usuario']} | Password: {u['password']}")
        print("------------------------------------------")
    else:
        print("\nNo se generaron contraseñas nuevas, todos tenían una asignada.")

if __name__ == "__main__":
    process_data()
