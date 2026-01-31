from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime
import io
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
CORS(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bitacora.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    nombre = db.Column(db.String(120))
    password = db.Column(db.String(120), nullable=False)
    rol = db.Column(db.String(20), nullable=False) # admin, asesor, lider, encargado, ayudante, cajero

class Tienda(db.Model):
    __tablename__ = 'tiendas'
    id = db.Column(db.Integer, primary_key=True)
    cr = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    distrito = db.Column(db.String(80))

class AsesorTienda(db.Model):
    __tablename__ = 'asesor_tienda'
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    tienda_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'), primary_key=True)

class Retiro(db.Model):
    __tablename__ = 'retiros'
    id = db.Column(db.Integer, primary_key=True)
    numero_retiro = db.Column(db.String(50), nullable=False)
    tienda_cr = db.Column(db.String(20), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    notas = db.Column(db.Text)
    imagen_fajilla = db.Column(db.Text) # Base64
    usuario_registro = db.Column(db.String(80), nullable=False)
    usuario_confirma = db.Column(db.String(80), nullable=False)
    fecha = db.Column(db.String(10), nullable=False)
    hora = db.Column(db.String(5), nullable=False)
    fecha_hora_registro = db.Column(db.String(30), nullable=False)

# --- RUTAS DE FRONTEND ---
@app.route('/')
def index():
    return send_file('bitacora.html')

# --- RUTAS DE LOGIN ---
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    usuario_input = data.get('usuario', '').strip().lower()
    password_input = data.get('password', '').strip()
    
    usuario = Usuario.query.filter(Usuario.usuario.ilike(usuario_input)).first()
    
    if usuario and usuario.password == password_input:
        tiendas = []
        asesor_nombre = "N/A"
        
        # Obtener tiendas asignadas para asesores y admins
        if usuario.rol.lower() in ['asesor', 'admin']:
            tiendas_ids = AsesorTienda.query.filter_by(usuario_id=usuario.id).all()
            for t_id in tiendas_ids:
                t = Tienda.query.get(t_id.tienda_id)
                if t:
                    tiendas.append({'cr': t.cr, 'nombre': t.nombre})
        elif usuario.rol.lower() in ['lider', 'encargado', 'ayudante', 'cajero']:
            # Buscar tienda asignada
            rel = AsesorTienda.query.filter_by(usuario_id=usuario.id).first()
            if rel:
                t = Tienda.query.get(rel.tienda_id)
                if t:
                    tiendas.append({'cr': t.cr, 'nombre': t.nombre})
                    # Buscar quién es el asesor de esta tienda
                    rel_asesor = AsesorTienda.query.join(Usuario).filter(
                        AsesorTienda.tienda_id == t.id,
                        Usuario.rol == 'asesor'
                    ).first()
                    if rel_asesor:
                        asesor_obj = Usuario.query.get(rel_asesor.usuario_id)
                        asesor_nombre = asesor_obj.nombre if asesor_obj else "N/A"

        return jsonify({
            'success': True,
            'user': {
                'id': usuario.id,
                'usuario': usuario.usuario,
                'nombre': usuario.nombre,
                'rol': usuario.rol.lower(),
                'tiendas': tiendas,
                'cr_defecto': tiendas[0]['cr'] if tiendas else 'SIN_CR',
                'asesor_nombre': asesor_nombre
            }
        })
    
    return jsonify({'success': False, 'message': 'Credenciales inválidas'}), 401

# --- CRUD DE USUARIOS ---
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    admin_id = request.args.get('admin_id')
    rol_solicitante = request.args.get('rol', '').lower()
    cr_solicitante = request.args.get('cr', '')

    if rol_solicitante == 'admin':
        usuarios = Usuario.query.all()
    elif rol_solicitante == 'asesor':
        # Ver lideres y colaboradores de sus tiendas
        tiendas_ids = [t.tienda_id for t in AsesorTienda.query.filter_by(usuario_id=admin_id).all()]
        usuarios_ids = [rel.usuario_id for rel in AsesorTienda.query.filter(AsesorTienda.tienda_id.in_(tiendas_ids)).all()]
        usuarios = Usuario.query.filter(Usuario.id.in_(usuarios_ids)).all()
        # Excluir al propio asesor de la lista si se desea, o dejarlo
        usuarios = [u for u in usuarios if u.id != int(admin_id)]
    elif rol_solicitante == 'lider':
        # Ver solo colaboradores de su tienda
        # 1. Obtener la tienda del lider desde AsesorTienda
        rel = AsesorTienda.query.filter_by(usuario_id=admin_id).first()
        if rel:
            tienda_id = rel.tienda_id
            usuarios_ids = [r.usuario_id for r in AsesorTienda.query.filter_by(tienda_id=tienda_id).all()]
            usuarios = Usuario.query.filter(Usuario.id.in_(usuarios_ids), Usuario.rol.in_(['encargado', 'ayudante', 'cajero'])).all()
        else:
            usuarios = []
    else:
        return jsonify([]), 403

    return jsonify([{
        'id': u.id,
        'usuario': u.usuario,
        'nombre': u.nombre,
        'rol': u.rol,
        'password': u.password
    } for u in usuarios])

@app.route('/api/usuarios', methods=['POST'])
def add_usuario():
    data = request.json
    rol_creador = data.get('creador_rol', '').lower()
    cr_creador = data.get('creador_cr', '')
    
    nuevo_usuario = Usuario(
        usuario=data.get('usuario'),
        nombre=data.get('nombre'),
        password=data.get('password'),
        rol=data.get('rol').lower()
    )
    
    db.session.add(nuevo_usuario)
    db.session.flush() # Para obtener el ID

    # Si es lider, asignar automáticamente a su tienda
    if rol_creador == 'lider':
        rel_lider = AsesorTienda.query.filter_by(usuario_id=data.get('creador_id')).first()
        if rel_lider:
            rel = AsesorTienda(usuario_id=nuevo_usuario.id, tienda_id=rel_lider.tienda_id)
            db.session.add(rel)
    elif cr_creador:
        tienda = Tienda.query.filter_by(cr=cr_creador).first()
        if tienda:
            rel = AsesorTienda(usuario_id=nuevo_usuario.id, tienda_id=tienda.id)
            db.session.add(rel)

    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/usuarios/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.json
    u = Usuario.query.get(id)
    if u:
        u.nombre = data.get('nombre', u.nombre)
        u.usuario = data.get('usuario', u.usuario)
        if data.get('password'):
            u.password = data.get('password')
        u.rol = data.get('rol', u.rol).lower()
        
        # Si se cambió la tienda (solo para asesores/admin)
        nueva_tienda_cr = data.get('tienda_cr')
        if nueva_tienda_cr:
            tienda = Tienda.query.filter_by(cr=nueva_tienda_cr).first()
            if tienda:
                rel = AsesorTienda.query.filter_by(usuario_id=id).first()
                if rel:
                    rel.tienda_id = tienda.id
                else:
                    nueva_rel = AsesorTienda(usuario_id=id, tienda_id=tienda.id)
                    db.session.add(nueva_rel)
        
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    u = Usuario.query.get(id)
    if u:
        AsesorTienda.query.filter_by(usuario_id=id).delete()
        db.session.delete(u)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/tiendas', methods=['GET'])
def get_tiendas():
    usuario_id = request.args.get('usuario_id')
    rol = request.args.get('rol', '').lower()

    if rol == 'admin':
        tiendas = Tienda.query.all()
    else:
        # Asesores y Lideres ven sus tiendas asignadas
        tiendas_ids = [t.tienda_id for t in AsesorTienda.query.filter_by(usuario_id=usuario_id).all()]
        tiendas = Tienda.query.filter(Tienda.id.in_(tiendas_ids)).all()

    return jsonify([{'cr': t.cr, 'nombre': t.nombre} for t in tiendas])

@app.route('/api/colaboradores', methods=['GET'])
def get_colaboradores():
    usuario_id = request.args.get('usuario_id')
    rol = request.args.get('rol', '').lower()
    cr = request.args.get('cr', '')

    if rol == 'admin':
        usuarios = Usuario.query.all()
    elif rol == 'asesor':
        tiendas_ids = [t.tienda_id for t in AsesorTienda.query.filter_by(usuario_id=usuario_id).all()]
        usuarios_ids = [rel.usuario_id for rel in AsesorTienda.query.filter(AsesorTienda.tienda_id.in_(tiendas_ids)).all()]
        usuarios = Usuario.query.filter(Usuario.id.in_(usuarios_ids)).all()
    else:
        # Lider ve a todos en su tienda
        tienda = Tienda.query.filter_by(cr=cr).first()
        if tienda:
            usuarios_ids = [rel.usuario_id for rel in AsesorTienda.query.filter_by(tienda_id=tienda.id).all()]
            usuarios = Usuario.query.filter(Usuario.id.in_(usuarios_ids)).all()
        else:
            usuarios = []

    return jsonify([{'usuario': u.usuario, 'nombre': u.nombre} for u in usuarios])

# --- CRUD DE TIENDAS ---
@app.route('/api/tiendas_admin', methods=['GET'])
def get_tiendas_admin():
    tiendas = Tienda.query.all()
    return jsonify([{
        'id': t.id,
        'cr': t.cr,
        'nombre': t.nombre,
        'distrito': t.distrito
    } for t in tiendas])

@app.route('/api/tiendas_admin', methods=['POST'])
def add_tienda():
    data = request.json
    nueva_tienda = Tienda(
        cr=data.get('cr').upper(),
        nombre=data.get('nombre'),
        distrito=data.get('distrito')
    )
    db.session.add(nueva_tienda)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/tiendas_admin/<int:id>', methods=['PUT'])
def update_tienda(id):
    data = request.json
    t = Tienda.query.get(id)
    if t:
        t.cr = data.get('cr').upper()
        t.nombre = data.get('nombre')
        t.distrito = data.get('distrito')
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/tiendas_admin/<int:id>', methods=['DELETE'])
def delete_tienda(id):
    t = Tienda.query.get(id)
    if t:
        # Eliminar relaciones y retiros asociados si fuera necesario
        AsesorTienda.query.filter_by(tienda_id=id).delete()
        db.session.delete(t)
        db.session.commit()
    return jsonify({'success': True})

# --- RUTAS DE RETIROS ---
@app.route('/api/retiros', methods=['GET'])
def get_retiros():
    usuario_id = request.args.get('usuario_id')
    rol = request.args.get('rol', '').lower()
    cr = request.args.get('cr')

    query = Retiro.query
    if rol in ['lider', 'encargado', 'ayudante', 'cajero']:
        # Si es lider ve todo lo de su tienda
        if rol == 'lider':
            query = query.filter_by(tienda_cr=cr)
        else:
            # Encargado, ayudante, cajero ven sus propios retiros
            query = query.filter_by(usuario_registro=request.args.get('usuario_nombre'))
    elif rol == 'asesor':
        tiendas_ids = AsesorTienda.query.filter_by(usuario_id=usuario_id).all()
        crs = [Tienda.query.get(t.tienda_id).cr for t in tiendas_ids]
        query = query.filter(Retiro.tienda_cr.in_(crs))
    
    retiros = query.order_by(Retiro.fecha_hora_registro.desc()).all()
    return jsonify([{
        'id': r.id, 'numeroRetiro': r.numero_retiro, 'tienda': r.tienda_cr,
        'monto': r.monto, 'notas': r.notas, 'imagenFajilla': r.imagen_fajilla,
        'colaborador': r.usuario_registro, 'confirmaUsuario': r.usuario_confirma,
        'fecha': r.fecha, 'hora': r.hora
    } for r in retiros])

@app.route('/api/retiros', methods=['POST'])
def create_retiro():
    data = request.json
    if data.get('rol', '').lower() in ['admin', 'asesor']:
        return jsonify({'success': False, 'message': 'No tienes permiso para retirar'}), 403
    
    confirmador = Usuario.query.filter_by(usuario=data.get('confirmaUsuario')).first()
    if not confirmador or confirmador.password != data.get('confirmaPassword'):
        return jsonify({'success': False, 'message': 'Confirmación inválida'}), 401

    now = datetime.now()
    nuevo = Retiro(
        numero_retiro=data.get('numeroRetiro'), tienda_cr=data.get('tienda'),
        monto=float(data.get('monto')), notas=data.get('notas'),
        imagen_fajilla=data.get('imagenFajilla'), usuario_registro=data.get('usuario_registro'),
        usuario_confirma=data.get('confirmaUsuario'), fecha=now.strftime('%Y-%m-%d'),
        hora=now.strftime('%H:%M'), fecha_hora_registro=now.isoformat()
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify({'success': True})

# --- EXPORTACIÓN ---
@app.route('/api/export/excel', methods=['POST'])
def export_excel():
    data = request.json
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Retiros')
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='reporte_retiros.xlsx')

@app.route('/api/export/pdf', methods=['POST'])
def export_pdf():
    data = request.json
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(letter))
    elements = []
    
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Reporte de Bitácora de Retiros Parciales", styles['Title']))
    
    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([str(row[h]) for h in headers])
        
        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
    
    doc.build(elements)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name='reporte_retiros.pdf')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
