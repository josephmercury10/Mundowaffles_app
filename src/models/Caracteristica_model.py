from utils.db import db
from datetime import datetime
from decimal import Decimal


class Caracteristica(db.Model):
    __tablename__ = 'caracteristicas'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(60), nullable=False)
    descripcion = db.Column(db.String(255), nullable=True)
    estado = db.Column(db.SmallInteger, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    # categorias = db.relationship('Categoria', backref='caracteristica', lazy=True, cascade='all, delete-orphan')
    #marcas = db.relationship('Marca', backref='caracteristica', lazy=True, cascade='all, delete-orphan')
    #presentaciones = db.relationship('Presentacion', backref='caracteristica', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }