import pandas as pd
from app import app, db, Usuario, Tienda, AsesorTienda
import os

def sync_relationships():
    with app.app_context():
        print("Iniciando sincronización de tiendas y asesores desde TTIENDAS.xlsx...")
        
        # Leer el Excel
        try:
            df = pd.read_excel('TTIENDAS.xlsx')
        except Exception as e:
            print(f"Error al leer TTIENDAS.xlsx: {e}")
            return

        # Limpiar nombres de columnas (quitar espacios al inicio/final)
        df.columns = [c.strip() for c in df.columns]
        
        # Columnas esperadas: 'CR TIENDA', 'NOMBRE TIENDA', 'ASESOR'
        col_cr = 'CR TIENDA'
        col_nombre = 'NOMBRE TIENDA'
        col_asesor = 'ASESOR'

        count_tiendas = 0
        count_rels = 0
        count_asesores_creados = 0

        for index, row in df.iterrows():
            cr = str(row[col_cr]).strip()
            nombre_tienda = str(row[col_nombre]).strip()
            nombre_asesor = str(row[col_asesor]).strip()

            if not cr or cr == 'nan':
                continue

            # 1. Asegurar que la tienda existe
            tienda = Tienda.query.filter_by(cr=cr).first()
            if not tienda:
                tienda = Tienda(cr=cr, nombre=nombre_tienda)
                db.session.add(tienda)
                db.session.flush()
                count_tiendas += 1
            
            # 2. Asegurar que el asesor existe como usuario
            # Buscamos por nombre ya que el Excel no trae el email/usuario
            # Si no existe, lo creamos con un usuario genérico basado en su nombre
            asesor = Usuario.query.filter(Usuario.nombre.ilike(nombre_asesor)).first()
            
            if not asesor and nombre_asesor and nombre_asesor != 'nan':
                # Crear usuario de asesor si no existe
                # Formato: nombre.apellido@oxxo.com (simplificado)
                user_email = nombre_asesor.lower().replace(' ', '.') + "@oxxo.com"
                # Verificar si el email ya existe
                existing_user = Usuario.query.filter_by(usuario=user_email).first()
                if existing_user:
                    asesor = existing_user
                else:
                    asesor = Usuario(
                        usuario=user_email,
                        nombre=nombre_asesor,
                        password='Oxxo' + cr, # Password temporal
                        rol='asesor'
                    )
                    db.session.add(asesor)
                    db.session.flush()
                    count_asesores_creados += 1
                    print(f"Asesor creado: {nombre_asesor} ({user_email})")

            # 3. Crear la relación Asesor-Tienda
            if asesor and tienda:
                rel = AsesorTienda.query.filter_by(usuario_id=asesor.id, tienda_id=tienda.id).first()
                if not rel:
                    nueva_rel = AsesorTienda(usuario_id=asesor.id, tienda_id=tienda.id)
                    db.session.add(nueva_rel)
                    count_rels += 1

        db.session.commit()
        print(f"Sincronización completada:")
        print(f"- Tiendas nuevas: {count_tiendas}")
        print(f"- Asesores nuevos: {count_asesores_creados}")
        print(f"- Relaciones creadas: {count_rels}")

if __name__ == "__main__":
    sync_relationships()

