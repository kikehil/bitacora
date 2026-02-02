const Database = require('better-sqlite3');
const path = require('path');

// Configuración de la base de datos
const dbPath = path.resolve(__dirname, 'bitacora.db');
const db = new Database(dbPath, { verbose: console.log });

/**
 * Inicializa las tablas de la base de datos si no existen
 */
function initDatabase() {
    // Habilitar claves foráneas
    db.pragma('foreign_keys = ON');

    // Tabla de Usuarios
    db.prepare(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('ADMIN', 'ASESOR', 'COLABORADOR')) NOT NULL,
            name TEXT NOT NULL
        )
    `).run();

    // Tabla de Tiendas
    db.prepare(`
        CREATE TABLE IF NOT EXISTS stores (
            cr TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            advisor_id TEXT,
            FOREIGN KEY (advisor_id) REFERENCES users(username)
        )
    `).run();

    // Tabla de Retiros
    db.prepare(`
        CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cr TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            collaborator1 TEXT NOT NULL,
            collaborator2 TEXT NOT NULL,
            photo_url TEXT,
            FOREIGN KEY (cr) REFERENCES stores(cr)
        )
    `).run();

    console.log('✅ Estructura de base de datos configurada correctamente.');
}

/**
 * Cierra la conexión a la base de datos de forma segura
 */
function closeConnection() {
    if (db.open) {
        db.close();
        console.log('🔒 Conexión a la base de datos cerrada de forma segura.');
    }
}

// Inicializar al cargar el módulo
initDatabase();

module.exports = {
    db,
    closeConnection
};




