from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal
import json

db = SQLAlchemy()

class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    impuesto = db.Column(db.Numeric(8, 2), nullable=False)
    numero_comprobante = db.Column(db.String(255), nullable=False)
    total = db.Column(db.Numeric(8, 2), nullable=False)
    estado = db.Column(db.SmallInteger, nullable=False, default=1)
    cliente_id = db.Column(db.BigInteger, db.ForeignKey('clientes.id'), nullable=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    comprobante_id = db.Column(db.BigInteger, db.ForeignKey('comprobantes.id'), nullable=True)
    tipoventa_id = db.Column(db.BigInteger, db.ForeignKey('tipoventas.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    productos = db.relationship('ProductoVenta', backref='venta', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'fecha_hora': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'impuesto': float(self.impuesto) if self.impuesto else 0,
            'numero_comprobante': self.numero_comprobante,
            'total': float(self.total) if self.total else 0,
            'estado': self.estado,
            'cliente_id': self.cliente_id,
            'user_id': self.user_id,
            'comprobante_id': self.comprobante_id,
            'tipoventa_id': self.tipoventa_id,
            'cliente': self.cliente.to_dict() if self.cliente else None,
            'user': self.user.to_dict() if self.user else None,
            'comprobante': self.comprobante.to_dict() if self.comprobante else None,
            'tipo_venta': self.tipo_venta.to_dict() if self.tipo_venta else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }