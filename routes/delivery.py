from flask import Blueprint, request, jsonify, render_template, session, flash
from datetime import datetime
from src.models.Persona_model import Persona
from src.models.Cliente_model import Cliente
from src.models.repartidores_model import Repartidor
from src.models.Producto_model import Producto
from src.models.Venta_model import Venta
from src.models.Venta_model import ProductoVenta
from utils.db import db
from forms import DeliveryForm

delivery_bp = Blueprint('delivery', __name__, url_prefix='/delivery')

@delivery_bp.route('/', methods=['GET'])
def getDeliveries():
    form = DeliveryForm()
    return render_template('ventas/delivery/index.html', form=form)


# Ruta para mostrar el formulario de nuevo delivery
@delivery_bp.route('/nuevo_delivery', methods=['GET'])
def nuevo_delivery():
    form = DeliveryForm()
    form.repartidor.choices = [('', 'Seleccione...')] + [(r.id, r.persona.razon_social) for r in Repartidor.query.all()]
    return render_template('ventas/delivery/_partials/nuevo_delivery.html', form=form)


# Ruta para manejar el envío del formulario y mostrar el carrito
@delivery_bp.route('/carrito_delivery', methods=['POST'])
def save():
    form = DeliveryForm()
    form.repartidor.choices = [('', 'Seleccione...')] + [(r.id, r.persona.razon_social) for r in Repartidor.query.all()]
    
    if form.validate_on_submit():
        try:
            
            # Obtener datos del formulario
            cliente_id = request.form.get('cliente_id')
            envio = int(form.costo_envio.data.strip())
            
            # Si es nuevo cliente y se debe guardar
            if cliente_id == '':
                # Crear nueva persona
                persona = Persona(
                    razon_social=form.cliente.data,
                    direccion=form.direccion.data,
                    telefono=form.telefono.data,
                    tipo_persona="Persona natural",
                    documento_id=1,  # Valor por defecto
                    numero_documento="Sin documento"  # Valor por defecto
                )
                db.session.add(persona)
                db.session.flush()  # Para obtener el ID
                
                # Crear nuevo cliente
                cliente = Cliente(
                    persona_id=persona.id
                )
                db.session.add(cliente)
                db.session.flush()
                
                db.session.commit()
                
                cliente_id = cliente.id
            
            # Almacenar el cliente_id en sesión para usarlo en guardar_pedido
            if cliente_id:
                session['cliente_id'] = cliente_id
                
            cliente_data = {
                'id': cliente_id,
                'nombre': form.cliente.data,
                'telefono': form.telefono.data,
                'direccion': form.direccion.data,
            }
            
            pedido_data = {
                'tiempo_estimado': form.tiempo_estimado.data,
                'repartidor': form.repartidor.data,
                'comentarios': form.comentarios.data
            }
            

            # Inicializar carrito en sesión
            session['carrito'] = {}
            session['cliente_data'] = cliente_data
            session['costo_envio'] = envio
            
            productos = Producto.query.filter_by(estado=1).all()

            return render_template('ventas/delivery/_partials/carrito_optimizado.html', 
                                 productos=productos, 
                                 cliente=cliente_data,
                                 carrito_items=[],
                                 pedido=pedido_data,
                                 subtotal=0,
                                 envio=envio,
                                 total=0
                                 )
        except Exception as e:
            return jsonify({'error': str(e)}), 500


# Ruta para agregar un producto al carrito
@delivery_bp.route('/agregar_al_carrito', methods=['POST'])
def agregar_al_carrito():
    producto_id = request.form.get('producto_id')
    nombre = request.form.get('nombre')
    precio = float(request.form.get('precio'))
    
    # Obtener carrito de sesión
    carrito = session.get('carrito', {})
    
    if producto_id in carrito:
        carrito[producto_id]['cantidad'] += 1
    else:
        carrito[producto_id] = {
            'id': producto_id,
            'nombre': nombre,
            'precio': precio,
            'cantidad': 1
        }
    
    session['carrito'] = carrito
    
    # Calcular totales
    carrito_items = []
    subtotal = 0
    
    for item in carrito.values():
        item['subtotal'] = item['precio'] * item['cantidad']
        subtotal += item['subtotal']
        carrito_items.append(item)
    
    envio = session.get('costo_envio', 0)
    total = subtotal + envio

    return render_template('ventas/delivery/_partials/carrito_items.html',
                         carrito_items=carrito_items,
                         subtotal=subtotal,
                         envio=envio,
                         total=total)
    


# Ruta para actualizar la cantidad de un producto en el carrito
@delivery_bp.route('/actualizar_cantidad', methods=['POST'])
def actualizar_cantidad():
    item_id = request.form.get('item_id')
    accion = request.form.get('accion')
    
    carrito = session.get('carrito', {})
    
    if item_id in carrito:
        if accion == 'aumentar':
            carrito[item_id]['cantidad'] += 1
        elif accion == 'disminuir':
            carrito[item_id]['cantidad'] -= 1
            if carrito[item_id]['cantidad'] <= 0:
                del carrito[item_id]
    
    session['carrito'] = carrito
    
    # Recalcular y renderizar
    return render_carrito_actualizado()


# Ruta para eliminar un producto del carrito
@delivery_bp.route('/eliminar_del_carrito/<item_id>', methods=['DELETE'])
def eliminar_del_carrito(item_id):
    carrito = session.get('carrito', {})
    if item_id in carrito:
        del carrito[item_id]
    session['carrito'] = carrito
    
    return render_carrito_actualizado()


# Función auxiliar para renderizar el carrito actualizado
def render_carrito_actualizado():
    carrito = session.get('carrito', {})
    carrito_items = []
    subtotal = 0
    
    for item in carrito.values():
        item['subtotal'] = item['precio'] * item['cantidad']
        subtotal += item['subtotal']
        carrito_items.append(item)
    
    envio = session.get('costo_envio', 0)
    total = subtotal + envio

    return render_template('ventas/delivery/_partials/carrito_items.html',
                         carrito_items=carrito_items,
                         subtotal=subtotal,
                         envio=envio,
                         total=total)


# Ruta para guardar el pedido para que quede en estado "En preparación"
@delivery_bp.route('/finalizar_pedido', methods=['POST'])
def finalizar_pedido():
    try:
        carrito = session.get('carrito', {})
        cliente_data = session.get('cliente_data', {})
        pedido_data = session.get('pedido_data', {})
        envio = session.get('costo_envio', 0)
        
        if not carrito:
            return jsonify({'error': 'Carrito vacío'}), 400
        
        # Crear venta
        venta = Venta(
            fecha_hora=db.func.current_timestamp(),
            impuesto=0.19,
            numero_comprobante=f"V-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            total=sum(item['precio'] * item['cantidad'] for item in carrito.values()),
            estado=1,
            cliente_id=cliente_data.get('id'),
            user_id=1,
            tipoventa_id=2,
            estado_delivery=1,
            costo_envio=envio,
            repartidor_id=pedido_data.get('repartidor') if pedido_data.get('repartidor') else None,
            comentarios=pedido_data.get('comentarios'),
            tiempo_estimado=pedido_data.get('tiempo_estimado')
        )
        db.session.add(venta)
        db.session.flush()
        
        # Agregar productos
        for item in carrito.values():
            producto_venta = ProductoVenta(
                venta_id=venta.id,
                producto_id=item['id'],
                cantidad=item['cantidad'],
                precio_venta=item['precio'],
                descuento=0
            )
            db.session.add(producto_venta)
        
        db.session.commit()
        
        # Limpiar sesión
        session.pop('carrito', None)
        session.pop('cliente_data', None)
        session.pop('pedido_data', None)
        session.pop('costo_envio', None)

        return render_template('ventas/delivery/_partials/pedido_confirmado.html',
                             venta_id=venta.id)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@delivery_bp.route('/buscar_cliente_telefono', methods=['POST'])
def buscar_cliente_telefono():
    query = request.form.get('telefono', '').strip()
    
    if not query or len(query) < 3:
        return ""
    
    # Buscar clientes que coincidan con la búsqueda por teléfono
    clientes = db.session.query(Cliente).join(Persona).filter(
        Persona.telefono.like(f'%{query}%')
    ).limit(5).all()
    
    return render_template('ventas/delivery/_partials/clientes_resultados_telefono.html', 
                           clientes=clientes, 
                           query=query)
    
    
# Seccion que se encarga de mostrar y actualizar datos de los pedidos

@delivery_bp.route('/detalle_pedido/<int:pedido_id>', methods=['GET'])
def detalle_pedido(pedido_id):
    try:
        # Obtener el pedido y sus productos
        pedido = Venta.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404

        productos = ProductoVenta.query.filter_by(venta_id=pedido_id).all()
        cliente = Cliente.query.get(pedido.cliente_id)
        
        # Calcular el total incluyendo el costo de envío
        costo_envio = pedido.costo_envio if pedido.costo_envio is not None else 0
        total_con_envio = pedido.total + costo_envio

        return render_template('ventas/delivery/_partials/detalle_pedido.html',
                               pedido=pedido,
                               productos=productos,
                               total_con_envio=total_con_envio,
                               costo_envio=costo_envio,
                               cliente=cliente)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@delivery_bp.route('/pedidos_estado/<estado>', methods=['GET'])
def ventas_estado(estado):
    try:
        # Convertir el estado a un entero
        estado = int(estado)

        # Filtrar las ventas según el estado
        ventas = Venta.query.filter_by(estado_delivery=estado).all()

        # Renderizar un fragmento de HTML con las ventas
        return render_template('ventas/delivery/_partials/pedidos.html', ventas=ventas)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@delivery_bp.route('/cambiar_estado/<int:pedido_id>/<int:nuevo_estado>', methods=['POST'])
def cambiar_estado(pedido_id, nuevo_estado):
    try:
        # Validar que el estado sea válido (1, 2 o 3)
        if nuevo_estado not in [1, 2, 3]:
            return jsonify({'error': 'Estado no válido'}), 400

        # Obtener el pedido
        pedido = Venta.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404

        # Actualizar el estado
        pedido.estado_delivery = nuevo_estado
        db.session.commit()

        # Devolver el fragmento actualizado
        return render_template('ventas/delivery/_partials/estado_pedido.html', pedido=pedido)

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    




@delivery_bp.route('/pedido/<int:pedido_id>/producto/<int:producto_id>/actualizar', methods=['POST'])
def actualizar_producto_pedido(pedido_id, producto_id):
    """Actualiza la cantidad de un producto en un pedido en preparación"""
    try:
        pedido = Venta.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        # Solo permitir si está en preparación
        if pedido.estado_delivery != 1:
            return jsonify({'error': 'No se puede modificar un pedido enviado'}), 403
        
        producto_venta = ProductoVenta.query.get(producto_id)
        if not producto_venta or producto_venta.venta_id != pedido_id:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        accion = request.form.get('accion')
        
        if accion == 'aumentar':
            producto_venta.cantidad += 1
        elif accion == 'disminuir':
            producto_venta.cantidad -= 1
            if producto_venta.cantidad <= 0:
                db.session.delete(producto_venta)
        
        # Recalcular total del pedido
        productos_restantes = ProductoVenta.query.filter_by(venta_id=pedido_id).all()
        pedido.total = sum(float(p.precio_venta) * p.cantidad for p in productos_restantes)
        
        db.session.commit()
        
        # Retornar el partial actualizado
        return _render_items_pedido(pedido_id)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@delivery_bp.route('/pedido/<int:pedido_id>/producto/<int:producto_id>/eliminar', methods=['DELETE'])
def eliminar_producto_pedido(pedido_id, producto_id):
    """Elimina un producto de un pedido en preparación"""
    try:
        pedido = Venta.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        if pedido.estado_delivery != 1:
            return jsonify({'error': 'No se puede modificar un pedido enviado'}), 403
        
        producto_venta = ProductoVenta.query.get(producto_id)
        if not producto_venta or producto_venta.venta_id != pedido_id:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        db.session.delete(producto_venta)
        
        # Recalcular total
        productos_restantes = ProductoVenta.query.filter_by(venta_id=pedido_id).all()
        pedido.total = sum(float(p.precio_venta) * p.cantidad for p in productos_restantes)
        
        db.session.commit()
        
        return _render_items_pedido(pedido_id)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def _render_items_pedido(pedido_id):
    """Función auxiliar para renderizar los items del pedido"""
    pedido = Venta.query.get(pedido_id)
    productos = ProductoVenta.query.filter_by(venta_id=pedido_id).all()
    costo_envio = pedido.costo_envio if pedido.costo_envio else 0
    total_con_envio = float(pedido.total) + float(costo_envio)
    
    return render_template('ventas/delivery/_partials/items_pedido.html',
                          pedido=pedido,
                          productos=productos,
                          total_con_envio=total_con_envio)
    
    
@delivery_bp.route('/pedido/<int:pedido_id>/productos_disponibles', methods=['GET'])
def productos_disponibles(pedido_id):
    """Retorna la lista de productos disponibles para agregar al pedido"""
    try:
        pedido = Venta.query.get(pedido_id)
        if not pedido or pedido.estado_delivery != 1:
            return '', 403
        
        # Obtener productos activos
        productos = Producto.query.filter_by(estado=1).all()
        
        return render_template('ventas/delivery/_partials/productos_disponibles.html',
                              productos=productos,
                              pedido_id=pedido_id)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@delivery_bp.route('/pedido/<int:pedido_id>/agregar_producto', methods=['POST'])
def agregar_producto_pedido(pedido_id):
    """Agrega un nuevo producto al pedido en preparación"""
    try:
        pedido = Venta.query.get(pedido_id)
        if not pedido:
            return jsonify({'error': 'Pedido no encontrado'}), 404
        
        if pedido.estado_delivery != 1:
            return jsonify({'error': 'No se puede modificar un pedido enviado'}), 403
        
        producto_id = request.form.get('producto_id')
        producto = Producto.query.get(producto_id)
        
        if not producto:
            return jsonify({'error': 'Producto no encontrado'}), 404
        
        # Verificar si el producto ya existe en el pedido
        producto_existente = ProductoVenta.query.filter_by(
            venta_id=pedido_id,
            producto_id=producto_id
        ).first()
        
        if producto_existente:
            # Si ya existe, aumentar cantidad
            producto_existente.cantidad += 1
        else:
            # Si no existe, crear nuevo registro
            nuevo_producto = ProductoVenta(
                venta_id=pedido_id,
                producto_id=producto_id,
                cantidad=1,
                precio_venta=producto.precio,
                descuento=0
            )
            db.session.add(nuevo_producto)
        
        # Recalcular total del pedido
        db.session.flush()
        productos_pedido = ProductoVenta.query.filter_by(venta_id=pedido_id).all()
        pedido.total = sum(float(p.precio_venta) * p.cantidad for p in productos_pedido)
        
        db.session.commit()
        
        return _render_items_pedido(pedido_id)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
    
    