from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from decimal import Decimal
import json

db = SQLAlchemy()

class ProductoVenta(db.Model):
    __tablename__ = 'producto_venta'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    venta_id = db.Column(db.BigInteger, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.BigInteger, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    descuento = db.Column(db.Numeric(8, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'venta_id': self.venta_id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'precio_venta': float(self.precio_venta) if self.precio_venta else 0,
            'descuento': float(self.descuento) if self.descuento else 0,
            'producto': self.producto.to_dict() if self.producto else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }