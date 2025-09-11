from flask import Blueprint, jsonify, render_template, request
from forms import DeliveryForm
from src.models import Producto_model
from utils.db import db

pruebas_bp = Blueprint('pruebas', __name__, url_prefix='/pruebas')

@pruebas_bp.route('/')
def prueba():
    form = DeliveryForm()
    return render_template('ventas/prueba.html', form=form)

@pruebas_bp.route('/save', methods=['POST'])
def save():
    form = DeliveryForm()
    if form.validate_on_submit():
        # Aquí puedes manejar la lógica para guardar los datos del formulario
        productos = Producto_model.Producto.query.all()
        return render_template('ventas/_partials/carrito.html', form=form, productos=productos)
    return jsonify({'errors': form.errors}), 400

@pruebas_bp.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    producto_id = request.form.get('id')
    nombre = request.form.get('nombre')
    precio = request.form.get('precio')

    #print(f"Producto ID: {producto_id}, Nombre: {nombre}, Precio: {precio}")

    return render_template('ventas/_partials/producto_item.html',
                         producto={
                             'id': producto_id,
                             'nombre': nombre,
                             'precio': precio
                         })
