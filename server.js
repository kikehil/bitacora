const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

const app = express();
const PORT = process.env.PORT || 5000;

// Conexión a la base de datos
const db = new Database('bitacora.db');

// Middleware
app.use(cors());
app.use(express.json());

// Configuración de Multer para fotos de fajillas
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        const uploadDir = 'uploads/';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir);
        }
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const cr = req.body.cr || 'SNC';
        const now = new Date();
        const dateStr = now.toISOString().split('T')[0].replace(/-/g, '');
        const timeStr = now.toTimeString().split(' ')[0].replace(/:/g, '').slice(0, 4);
        cb(null, `${cr}_${dateStr}_${timeStr}${path.extname(file.originalname)}`);
    }
});

const upload = multer({ storage: storage });

// Servir archivos estáticos
app.use('/uploads', express.static('uploads'));

// Servir el frontend (si existe una carpeta build o el archivo bitacora.html)
app.get('/', (req, res) => {
    const htmlPath = path.join(__dirname, 'bitacora.html');
    if (fs.existsSync(htmlPath)) {
        res.sendFile(htmlPath);
    } else {
        res.send('Servidor API OXXO Operando. Por favor, abre el frontend.');
    }
});

// --- ENDPOINTS ---

// 1. LOGIN
app.post('/api/login', (req, res) => {
    // ... (se mantiene igual)
});

// 4. GESTIÓN DE USUARIOS (ADMIN & ASESOR)
app.get('/api/users', (req, res) => {
    const { requester_role, requester_email } = req.query;
    
    console.log('--- DEBUG GESTIÓN USUARIOS ---');
    console.log('Solicitante:', requester_email);
    console.log('Rol:', requester_role);
    
    try {
        if (requester_role === 'ADMIN') {
            const users = db.prepare('SELECT id, username, name, role, cr FROM users').all();
            return res.json(users);
        } 
        
        if (requester_role === 'ASESOR') {
            // 1. Obtener los CRs que este asesor supervisa
            const advisorStores = db.prepare('SELECT cr FROM stores WHERE advisor_id = ?').all(requester_email);
            const crList = advisorStores.map(s => s.cr);
            
            console.log('CRs supervisados por este asesor:', crList.length);

            if (crList.length === 0) {
                console.log('Aviso: El asesor no tiene tiendas asignadas.');
                return res.json([]);
            }

            // 2. Obtener solo los usuarios que pertenecen a esos CRs
            // IMPORTANTE: Si un usuario no tiene CR (null), NO se mostrará al asesor
            const placeholders = crList.map(() => '?').join(',');
            const users = db.prepare(`
                SELECT id, username, name, role, cr 
                FROM users 
                WHERE cr IN (${placeholders})
                AND role NOT IN ('ADMIN', 'ASESOR')
            `).all(...crList);

            console.log(`Usuarios operativos encontrados para este asesor: ${users.length}`);
            return res.json(users);
        }

        return res.status(403).json({ message: 'No autorizado' });
    } catch (error) {
        console.error('ERROR CRÍTICO EN GET /api/users:', error);
        res.status(500).json({ message: 'Error de seguridad al obtener usuarios' });
    }
});

app.post('/api/users/register', (req, res) => {
    const { username, password, name, role, cr, requester_role, requester_email } = req.body;
    
    try {
        // VALIDACIÓN DE SEGURIDAD EN ALTA
        if (requester_role === 'ASESOR') {
            // 1. Bloqueo de roles no permitidos
            if (['ADMIN', 'ASESOR'].includes(role.toUpperCase())) {
                return res.status(403).json({ success: false, message: 'No tienes permiso para asignar este rol' });
            }
            // 2. Verificar que el CR enviado pertenezca al Asesor
            const storeOwned = db.prepare('SELECT cr FROM stores WHERE cr = ? AND advisor_id = ?').get(cr, requester_email);
            if (!storeOwned) {
                return res.status(403).json({ success: false, message: 'El CR enviado no está bajo tu supervisión' });
            }
        }

        const existing = db.prepare('SELECT username FROM users WHERE username = ?').get(username);
        if (existing) {
            return res.status(400).json({ success: false, message: 'El correo electrónico ya está registrado' });
        }

        const insert = db.prepare('INSERT INTO users (username, password, name, role, cr) VALUES (?, ?, ?, ?, ?)');
        const result = insert.run(username, password, name, role.toUpperCase(), cr);

        console.log(`[ALTA SEGURA] Usuario ${role} creado para CR ${cr} por Asesor ${requester_email}`);
        res.json({ success: true, id: result.lastInsertRowid, message: 'Usuario registrado correctamente' });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Error en el servidor: ' + error.message });
    }
});

app.delete('/api/users/:id', (req, res) => {
    const { id } = req.params;
    try {
        db.prepare('DELETE FROM users WHERE id = ?').run(id);
        res.json({ success: true, message: 'Usuario eliminado' });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Error al eliminar' });
    }
});

// 4.1 RESET PASSWORD (ADMIN ONLY)
app.patch('/api/users/reset-password', (req, res) => {
    const { username, newPassword } = req.body;
    
    try {
        const update = db.prepare('UPDATE users SET password = ? WHERE username = ?');
        const result = update.run(newPassword, username);

        if (result.changes > 0) {
            console.log(`[ADMIN] Password reseteado para el usuario: ${username}`);
            res.json({ success: true, message: 'Contraseña actualizada correctamente' });
        } else {
            res.status(404).json({ success: false, message: 'Usuario no encontrado' });
        }
    } catch (error) {
        res.status(500).json({ success: false, message: 'Error al resetear password: ' + error.message });
    }
});

// 2. TIENDAS POR ASESOR
app.get('/api/advisor/stores/:email', (req, res) => {
    const { email } = req.params;
    
    try {
        const stores = db.prepare('SELECT cr, name FROM stores WHERE advisor_id = ?').all(email);
        res.json(stores);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener tiendas' });
    }
});

// 2.1 ESTADÍSTICAS DEL ASESOR (NUEVO)
app.get('/api/advisor/stats/:email', (req, res) => {
    const { email } = req.params;
    const today = new Date().toISOString().split('T')[0];
    
    try {
        // Conteo de tiendas
        const storesCount = db.prepare('SELECT COUNT(*) as total FROM stores WHERE advisor_id = ?').get(email);
        
        // Suma de retiros de hoy para sus tiendas
        const todayTotal = db.prepare(`
            SELECT SUM(w.amount) as total 
            FROM withdrawals w
            JOIN stores s ON w.cr = s.cr
            WHERE s.advisor_id = ? AND w.date = ?
        `).get(email, today);

        res.json({
            total_stores: storesCount.total || 0,
            today_amount: todayTotal.total || 0
        });
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener estadísticas: ' + error.message });
    }
});

// 2.2 HISTORIAL DE RETIROS POR TIENDA (NUEVO)
app.get('/api/withdrawals/:cr', (req, res) => {
    const { cr } = req.params;
    
    try {
        const history = db.prepare(`
            SELECT id, amount, date, time, collaborator1, collaborator2, photo_url 
            FROM withdrawals 
            WHERE cr = ? 
            ORDER BY date DESC, time DESC
        `).all(cr);
        
        res.json(history);
    } catch (error) {
        res.status(500).json({ message: 'Error al obtener historial: ' + error.message });
    }
});

// 3. REGISTRO DE RETIRO DIRECTO CON EVIDENCIA
app.post('/api/withdrawals', upload.single('photo'), (req, res) => {
    const { cr, amount, collaborator1 } = req.body;
    const photo_url = req.file ? `/uploads/${req.file.filename}` : null;

    if (!cr || !amount || !collaborator1 || !photo_url) {
        return res.status(400).json({ success: false, message: 'Faltan datos obligatorios o evidencia fotográfica' });
    }

    try {
        const now = new Date();
        const date = now.toISOString().split('T')[0];
        const time = now.toTimeString().split(' ')[0].slice(0, 5);

        const insert = db.prepare(`
            INSERT INTO withdrawals (cr, amount, date, time, collaborator1, collaborator2, photo_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `);

        // En registro directo, collaborator2 se guarda como 'DIRECTO' o null
        const result = insert.run(cr, parseFloat(amount), date, time, collaborator1, 'DIRECTO', photo_url);

        res.json({ 
            success: true, 
            id: result.lastInsertRowid,
            folio: `RET-${cr}-${Date.now().toString().slice(-6)}`,
            message: 'Retiro registrado correctamente en Bitácora Digital'
        });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Error al registrar retiro: ' + error.message });
    }
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`🚀 Servidor backend OXXO corriendo en http://localhost:${PORT}`);
});
