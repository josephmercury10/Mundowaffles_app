from flask import Blueprint,  render_template, redirect, url_for, flash, request
from src.models.Producto_model import Producto
from src.models.Caracteristica_model import Caracteristica
from src.models.Marca_model import Marca
from src.models.Presentacion_model import Presentacion
from src.models.Categoria_model import Categoria

from utils.db import db
from forms import ProductoForm

productos_bp = Blueprint('productos', __name__ , url_prefix='/productos')

@productos_bp.route('/')
def get_productos():
    
    productos = Producto.query.all()

    return render_template('productos/productos.html', productos=productos)


@productos_bp.route('/add', methods=['GET', 'POST'])
def create_producto():
    form = ProductoForm()
    form.marcas.choices = [(str(marca.id), marca.caracteristica.nombre) 
                          for marca in Marca.query
                          .join(Marca.caracteristica)
                          .filter(Caracteristica.estado == 1)
                          .all()]
    
    form.presentaciones.choices = [(str(p.id), p.caracteristica.nombre)
                                    for p in Presentacion.query
                                    .join(Presentacion.caracteristica)
                                    .filter(Caracteristica.estado == 1)
                                    .all()]
    
    form.categorias.choices = [(str(c.id), c.caracteristica.nombre)
                                for c in Categoria.query
                                .join(Categoria.caracteristica)
                                .filter(Caracteristica.estado == 1)
                                .all()]

    if request.method == 'POST':
        # Aquí iría la lógica para manejar el formulario y crear un nuevo producto
        if form.validate_on_submit():
            # Procesar y guardar el nuevo producto
            
            productoID = Producto.query.filter_by(codigo=form.codigo.data).first()
            if productoID is None:
                
                try:
                    nuevo_producto = Producto(
                        codigo=form.codigo.data,
                        nombre=form.nombre.data,
                        descripcion=form.descripcion.data,
                        fecha_vencimiento=form.fechaVencimiento.data,
                        img_path=form.imagen.data.filename if form.imagen.data else None,
                        marca_id=form.marcas.data,
                        presentacione_id=form.presentaciones.data
                    )                        
                    db.session.add(nuevo_producto)
                    db.session.flush()
                    
                    nuevo_producto.categorias = [Categoria.query.get(int(categoria_id)) for categoria_id in form.categorias.data]
                    db.session.commit()
                    flash('Producto creado exitosamente', 'success')
                    return redirect(url_for('productos.get_productos'))
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"Error: {str(e)}")

            return redirect(url_for('productos.get_productos'))
        else:
            print('Error en el formulario. Por favor, revisa los datos ingresados.')

    return render_template('productos/create.html', form=form)


