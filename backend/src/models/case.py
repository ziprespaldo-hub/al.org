from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from src.models.user import db

class Case(db.Model):
    __tablename__ = 'casos'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_caso = db.Column(db.String(50), unique=True, nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    abogado_asignado_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    estado = db.Column(db.String(20), nullable=False, default='pendiente')
    prioridad = db.Column(db.String(20), nullable=False, default='media')
    fecha_apertura = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cierre = db.Column(db.DateTime)
    
    # Relaciones
    cliente = db.relationship('Client', backref='casos')
    abogado = db.relationship('User', backref='casos_asignados')
    equipos = db.relationship('Equipment', backref='caso', cascade='all, delete-orphan')
    eventos = db.relationship('AgendaEvent', backref='caso')
    transacciones = db.relationship('Transaction', backref='caso')
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero_caso': self.numero_caso,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'cliente_id': self.cliente_id,
            'cliente_nombre': self.cliente.nombre_completo if self.cliente else None,
            'abogado_asignado_id': self.abogado_asignado_id,
            'abogado_nombre': self.abogado.nombre_completo if self.abogado else None,
            'estado': self.estado,
            'prioridad': self.prioridad,
            'fecha_apertura': self.fecha_apertura.isoformat() if self.fecha_apertura else None,
            'fecha_cierre': self.fecha_cierre.isoformat() if self.fecha_cierre else None
        }

class Client(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.Text)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre_completo': self.nombre_completo,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class Equipment(db.Model):
    __tablename__ = 'equipos'
    
    id = db.Column(db.Integer, primary_key=True)
    caso_id = db.Column(db.Integer, db.ForeignKey('casos.id'), nullable=False)
    tipo_equipo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100))
    imei = db.Column(db.String(20))
    condicion_fisica = db.Column(db.String(20))
    descripcion_danos = db.Column(db.Text)
    accesorios = db.Column(db.Text)
    recibido_de = db.Column(db.String(200))
    fecha_recepcion = db.Column(db.DateTime, default=datetime.utcnow)
    notas_custodia = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'caso_id': self.caso_id,
            'tipo_equipo': self.tipo_equipo,
            'marca': self.marca,
            'modelo': self.modelo,
            'numero_serie': self.numero_serie,
            'imei': self.imei,
            'condicion_fisica': self.condicion_fisica,
            'descripcion_danos': self.descripcion_danos,
            'accesorios': self.accesorios,
            'recibido_de': self.recibido_de,
            'fecha_recepcion': self.fecha_recepcion.isoformat() if self.fecha_recepcion else None,
            'notas_custodia': self.notas_custodia
        }

class AgendaEvent(db.Model):
    __tablename__ = 'agenda_eventos'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime)
    ubicacion = db.Column(db.String(200))
    tipo_evento = db.Column(db.String(50))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    caso_id = db.Column(db.Integer, db.ForeignKey('casos.id'))
    
    usuario = db.relationship('User', backref='eventos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'fecha_inicio': self.fecha_inicio.isoformat() if self.fecha_inicio else None,
            'fecha_fin': self.fecha_fin.isoformat() if self.fecha_fin else None,
            'ubicacion': self.ubicacion,
            'tipo_evento': self.tipo_evento,
            'usuario_id': self.usuario_id,
            'caso_id': self.caso_id
        }

class Transaction(db.Model):
    __tablename__ = 'transacciones'
    
    id = db.Column(db.Integer, primary_key=True)
    caso_id = db.Column(db.Integer, db.ForeignKey('casos.id'))
    tipo = db.Column(db.String(20), nullable=False)  # 'ingreso', 'gasto'
    concepto = db.Column(db.String(200), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    usuario = db.relationship('User', backref='transacciones')
    
    def to_dict(self):
        return {
            'id': self.id,
            'caso_id': self.caso_id,
            'tipo': self.tipo,
            'concepto': self.concepto,
            'monto': self.monto,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'usuario_id': self.usuario_id
        }

class Contact(db.Model):
    __tablename__ = 'contactos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    asunto = db.Column(db.String(200))
    mensaje = db.Column(db.Text, nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    leido = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'asunto': self.asunto,
            'mensaje': self.mensaje,
            'fecha_envio': self.fecha_envio.isoformat() if self.fecha_envio else None,
            'leido': self.leido
        }

