const Database = require('better-sqlite3');
const xlsx = require('xlsx');
const fs = require('fs');

const db = new Database('bitacora.db');

function seed() {
    try {
        console.log('--- Iniciando carga de datos (Seeding por Correo) ---');

        // Limpieza total
        db.prepare('DELETE FROM withdrawals').run();
        db.prepare('DELETE FROM stores').run();
        db.prepare('DELETE FROM users').run();
        console.log('🧹 Base de datos limpia.');

        if (!fs.existsSync('seed_data.json')) {
            console.error('Error: No se encuentra seed_data.json');
            return;
        }
        const users = JSON.parse(fs.readFileSync('seed_data.json', 'utf8'));
        
        const insertUser = db.prepare(`
            INSERT INTO users (username, password, role, name)
            VALUES (?, ?, ?, ?)
        `);

        db.transaction(() => {
            for (const user of users) {
                insertUser.run(user.usuario, user.password, user.rol, user.nombre);
            }
        })();
        console.log(`✅ ${users.length} usuarios cargados.`);

        if (!fs.existsSync('TTIENDAS.xlsx')) {
            console.error('Error: No se encuentra TTIENDAS.xlsx');
            return;
        }

        const workbook = xlsx.readFile('TTIENDAS.xlsx');
        const sheet = workbook.Sheets[workbook.SheetNames[0]];
        const storesDataRaw = xlsx.utils.sheet_to_json(sheet, { defval: null });

        const storesData = storesDataRaw.map(row => {
            const newRow = {};
            for (let key in row) {
                newRow[key.toLowerCase().trim()] = row[key];
            }
            return newRow;
        });

        const advisorMap = new Map();
        users.forEach(u => advisorMap.set(u.nombre.toLowerCase().trim(), u.usuario));

        const insertStore = db.prepare(`
            INSERT INTO stores (cr, name, advisor_id)
            VALUES (?, ?, ?)
        `);

        let storesCount = 0;
        db.transaction(() => {
            for (const row of storesData) {
                const crKey = Object.keys(row).find(k => k.includes('cr'));
                // Buscamos específicamente la columna que contenga "nombre tienda"
                const nameKey = Object.keys(row).find(k => k.toLowerCase().includes('nombre tienda')) || 
                                Object.keys(row).find(k => k.includes('nombre') || k.includes('tienda'));
                const advisorKey = Object.keys(row).find(k => k.includes('asesor'));

                const cr = row[crKey];
                const nombreTienda = row[nameKey];
                const nombreAsesor = row[advisorKey];

                if (cr && cr.toString().trim() !== '') {
                    const advisorEmail = nombreAsesor ? advisorMap.get(nombreAsesor.toString().trim().toLowerCase()) : null;
                    insertStore.run(
                        cr.toString().trim(), 
                        (nombreTienda || cr).toString().trim(), 
                        advisorEmail
                    );
                    storesCount++;
                }
            }
        })();

        console.log(`✅ ${storesCount} tiendas cargadas y vinculadas.`);
        
        const orphanStores = db.prepare('SELECT COUNT(*) as count FROM stores WHERE advisor_id IS NULL').get();
        if (orphanStores.count > 0) {
            console.warn(`⚠️ Alerta: ${orphanStores.count} tiendas no encontraron su correo de asesor.`);
        }

    } catch (error) {
        console.error('❌ Error:', error.message);
    } finally {
        db.close();
    }
}

seed();
