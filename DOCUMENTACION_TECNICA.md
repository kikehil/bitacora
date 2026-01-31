# Documentación Técnica - OXXO Bitácora Digital

## 1. Arquitectura del Sistema
El sistema sigue una arquitectura de aplicación web de una sola página (SPA) con un backend de servicios REST.

- **Frontend:** HTML5, CSS3 (PulseTec Design System), React.js (v18) vía CDN.
- **Backend:** Python 3.x con Flask.
- **Base de Datos:** SQLite 3 (Archivo `bitacora.db`).
- **ORM:** SQLAlchemy para la gestión de modelos y relaciones.

## 2. Modelos de Datos (Base de Datos)
- **Usuario:** Almacena credenciales, nombres y roles (`admin`, `asesor`, `lider`, `encargado`, `ayudante`, `cajero`).
- **Tienda:** Catálogo de tiendas con CR, nombre y distrito.
- **AsesorTienda:** Tabla relacional que vincula usuarios con tiendas (Relación 1:N para asesores, 1:1 para operativos).
- **Retiro:** Registro de cada operación parcial, incluyendo monto, folio, usuarios involucrados y evidencia fotográfica (Base64).

## 3. Seguridad y Roles
El sistema implementa RBAC (Role-Based Access Control):
- **Admin:** Control total, gestión de todas las tiendas y todos los usuarios.
- **Asesor:** Gestión de líderes y colaboradores de sus tiendas asignadas. Reportes de sus tiendas.
- **Lider:** Gestión de colaboradores de su tienda. Registro de retiros y reportes de su tienda.
- **Operativos (Encargado/Ayudante/Cajero):** Registro de retiros y consulta de sus propios movimientos.

## 4. Endpoints Principales (API)
- `POST /api/login`: Autenticación y carga de sesión.
- `GET /api/retiros`: Obtención de registros filtrados por rol.
- `POST /api/retiros`: Creación de retiro con validación de segundo colaborador.
- `GET /api/usuarios`: Gestión de personal según jerarquía.
- `POST /api/export/excel` & `pdf`: Generación dinámica de reportes.

## 5. Despliegue (VPS)
- **Servidor Web:** Nginx (Proxy inverso).
- **WSGI:** Gunicorn ejecutando la app Flask.
- **Gestión de Procesos:** Systemd (servicio `bitacora.service`).

