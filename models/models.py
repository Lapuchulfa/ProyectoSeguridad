from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Longitud para password encriptada con hash

class Activo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)  # Ej: Hardware, Software, Redes, Datos, Personal
    descripcion = db.Column(db.Text, nullable=True)
    
    # Dimensiones de Valoración CID (Escala Magerit del 0 al 5)
    confidencialidad = db.Column(db.Integer, default=0)
    integridad = db.Column(db.Integer, default=0)
    disponibilidad = db.Column(db.Integer, default=0)
    
    valor_total = db.Column(db.Integer, default=0)

    # Relación: Un activo puede tener muchos riesgos asociados. 
    # Si se borra el activo, se borran sus riesgos en cascada.
    riesgos = db.relationship('Riesgo', backref='activo', lazy=True, cascade="all, delete-orphan")

class Riesgo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    activo_id = db.Column(db.Integer, db.ForeignKey('activo.id'), nullable=False)
    
    # Identificación según Magerit
    amenaza = db.Column(db.String(150), nullable=False)        # Ej: Acceso no autorizado, Fuego, Fuga de información
    vulnerabilidad = db.Column(db.String(150), nullable=False)   # Ej: Ausencia de políticas de contraseñas, Software desactualizado
    
    # Matriz de Análisis de Riesgos (Valores de probabilidad e impacto)
    probabilidad = db.Column(db.Integer, nullable=False)  # Escala 1 a 5
    impacto = db.Column(db.Integer, nullable=False)       # Escala 1 a 5
    nivel_riesgo = db.Column(db.Integer, nullable=False)  # Cálculo automático: Probabilidad * Impacto
    
    # Relaciones 1-a-1 de seguimiento: Un riesgo tiene un tratamiento específico y un único riesgo residual
    tratamiento = db.relationship('Tratamiento', backref='riesgo', uselist=False, cascade="all, delete-orphan")
    residual = db.relationship('RiesgoResidual', backref='riesgo', uselist=False, cascade="all, delete-orphan")
    
class Tratamiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    riesgo_id = db.Column(db.Integer, db.ForeignKey('riesgo.id'), nullable=False)
    
    # Estrategia de respuesta
    estrategia = db.Column(db.String(50), nullable=False)  # Mitigar, Transferir, Aceptar, Evitar
    
    # Mapeo y referencia con el estándar internacional
    control_iso27002 = db.Column(db.String(150), nullable=False) # Ej: "A.5.15 - Gestión de contraseñas"
    detalles_control = db.Column(db.Text, nullable=True)          # Descripción técnica de la solución/automatización propesta
    
    responsable = db.Column(db.String(100), nullable=False)       # Encargado de implementar/monitorear el control
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

class RiesgoResidual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    riesgo_id = db.Column(db.Integer, db.ForeignKey('riesgo.id'), nullable=False)
    
    # Nuevos valores estimados tras evaluar la eficiencia del control/salvaguarda implementado
    probabilidad_residual = db.Column(db.Integer, nullable=False)
    impacto_residual = db.Column(db.Integer, nullable=False)
    nivel_residual = db.Column(db.Integer, nullable=False) # Cálculo automático: Probabilidad_residual * Impacto_residual

class Observacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origen_modulo = db.Column(db.String(50), nullable=False)  # Ej: "Activos", "Riesgos", "Tratamiento"
    comentario = db.Column(db.Text, nullable=False)
    autor_nombre = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)