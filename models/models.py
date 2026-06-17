from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    activos = db.relationship('Activo', backref='usuario', lazy=True, cascade="all, delete-orphan")
    observaciones = db.relationship('Observacion', backref='usuario', lazy=True, cascade="all, delete-orphan")

class Activo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    confidencialidad = db.Column(db.Integer, default=0)
    integridad = db.Column(db.Integer, default=0)
    disponibilidad = db.Column(db.Integer, default=0)
    valor_total = db.Column(db.Integer, default=0)

    riesgos = db.relationship('Riesgo', backref='activo', lazy=True, cascade="all, delete-orphan")

class Riesgo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activo_id = db.Column(db.Integer, db.ForeignKey('activo.id'), nullable=False)

    amenaza = db.Column(db.String(150), nullable=False)
    vulnerabilidad = db.Column(db.String(150), nullable=False)

    probabilidad = db.Column(db.Integer, nullable=False)
    impacto = db.Column(db.Integer, nullable=False)
    nivel_riesgo = db.Column(db.Integer, nullable=False)

    tratamiento = db.relationship('Tratamiento', backref='riesgo', uselist=False, cascade="all, delete-orphan")
    residual = db.relationship('RiesgoResidual', backref='riesgo', uselist=False, cascade="all, delete-orphan")

class Tratamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    riesgo_id = db.Column(db.Integer, db.ForeignKey('riesgo.id'), nullable=False)

    estrategia = db.Column(db.String(50), nullable=False)
    control_iso27002 = db.Column(db.String(150), nullable=False)
    detalles_control = db.Column(db.Text, nullable=True)
    responsable = db.Column(db.String(100), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class RiesgoResidual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    riesgo_id = db.Column(db.Integer, db.ForeignKey('riesgo.id'), nullable=False)

    probabilidad_residual = db.Column(db.Integer, nullable=False)
    impacto_residual = db.Column(db.Integer, nullable=False)
    nivel_residual = db.Column(db.Integer, nullable=False)

class Observacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    origen_modulo = db.Column(db.String(50), nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    autor_nombre = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
