const xlsx = require('xlsx');
const fs = require('fs');

function generatePassword(length = 8) {
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    let retVal = "";
    for (let i = 0, n = charset.length; i < length; ++i) {
        retVal += charset.charAt(Math.floor(Math.random() * n));
    }
    return retVal;
}

function processFiles() {
    try {
        console.log('--- Iniciando procesamiento de datos (Identidad por Correo) ---');

        const usuariosFinales = [];
        const correosProcesados = new Set();
        let credencialesTexto = "=== CONFIDENCIAL - LISTADO DE ACCESOS PROYECTO BOCAO/OXXO ===\n";
        credencialesTexto += `Fecha de generación: ${new Date().toLocaleString()}\n`;
        credencialesTexto += "============================================================\n\n";

        if (!fs.existsSync('USUARIOS.xlsx')) {
            console.error('Error: No se encuentra el archivo USUARIOS.xlsx');
            return;
        }
        
        const workbookUsuarios = xlsx.readFile('USUARIOS.xlsx');
        const sheetUsuarios = workbookUsuarios.Sheets[workbookUsuarios.SheetNames[0]];
        const dataUsuarios = xlsx.utils.sheet_to_json(sheetUsuarios, { defval: null });

        const normalizedUsers = dataUsuarios.map(row => {
            const newRow = {};
            for (let key in row) {
                newRow[key.toLowerCase().trim()] = row[key];
            }
            return newRow;
        });

        normalizedUsers.forEach(row => {
            const nombreKey = Object.keys(row).find(k => k.includes('nombre'));
            const correoKey = Object.keys(row).find(k => k.includes('usuario') || k.includes('correo') || k.includes('email'));
            const passKey = Object.keys(row).find(k => k.includes('password') || k.includes('contraseña'));
            const rolKey = Object.keys(row).find(k => k.includes('rol'));

            const nombre = row[nombreKey] ? row[nombreKey].toString().trim() : 'Sin Nombre';
            const correo = row[correoKey] ? row[correoKey].toString().trim().toLowerCase() : null;
            const password = (row[passKey] && row[passKey].toString().trim() !== '') ? row[passKey].toString().trim() : generatePassword();
            const rol = row[rolKey] ? row[rolKey].toString().trim().toUpperCase() : 'ASESOR';

            if (correo && !correosProcesados.has(correo)) {
                const usuario = {
                    nombre: nombre,
                    rol: rol,
                    usuario: correo,
                    password: password
                };
                usuariosFinales.push(usuario);
                correosProcesados.add(correo);
                
                credencialesTexto += `Nombre: ${nombre}\nRol: ${rol}\nUsuario (Correo): ${correo}\nContraseña: ${password}\n---------------------------\n`;
            }
        });

        fs.writeFileSync('credenciales_maestras.txt', credencialesTexto);
        fs.writeFileSync('seed_data.json', JSON.stringify(usuariosFinales, null, 4));

        console.log(`✅ Se procesaron ${usuariosFinales.length} usuarios únicos.`);
        console.log('- Archivo "credenciales_maestras.txt" generado.');
        console.log('- Archivo "seed_data.json" generado.');

    } catch (error) {
        console.error('Error:', error.message);
    }
}

processFiles();
