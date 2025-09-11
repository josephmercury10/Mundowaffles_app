from datetime import datetime
from decimal import Decimal
from utils.db import db

class CategoriaProducto(db.Model):
    __tablename__ = 'categoria_producto'
    
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    producto_id = db.Column(db.BigInteger, db.ForeignKey('productos.id'), nullable=False)
    categoria_id = db.Column(db.BigInteger, db.ForeignKey('categorias.id'), nullable=False)
    
    # Relaciones directas
    producto = db.relationship("Producto", back_populates="categorias")
    categoria = db.relationship("Categoria", back_populates="productos")

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(50), nullable=False)
    nombre = db.Column(db.String(80), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    descripcion = db.Column(db.String(255), nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal('0.00'))
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    img_path = db.Column(db.String(255), nullable=True)
    estado = db.Column(db.SmallInteger, nullable=False, default=1)
    marca_id = db.Column(db.BigInteger, db.ForeignKey('marcas.id'), nullable=False)
    presentacione_id = db.Column(db.BigInteger, db.ForeignKey('presentaciones.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    categorias = db.relationship("CategoriaProducto", back_populates="producto")
    marca = db.relationship("Marca")
    presentacion = db.relationship("Presentacion")

    def __repr__(self):
        return f"<Producto(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}')>"