# Instrucciones para Agentes de IA - Mundo Waffles

## Descripción del Proyecto
Sistema POS (Punto de Venta) para restaurante de waffles desarrollado en Flask con MySQL. Maneja productos, ventas, delivery, clientes y características de productos.

## Arquitectura Principal

### Estructura de Capas
```
app.py                     # Punto de entrada, registra blueprints y configura Flask
├── routes/                # Blueprints con rutas y lógica de controladores
├── src/models/            # Modelos SQLAlchemy
├── forms.py               # Formularios WTForms centralizados
├── utils/                 # Helpers: db.py, filters.py, helpers_db.py
└── templates/             # Templates Jinja2 organizados por módulo
```

### Patrón de Modelos con Característica
Los modelos `Marca`, `Categoria`, `Presentacion` comparten un patrón común: heredan de `Caracteristica` mediante relación:
```python
# Ejemplo: src/models/Marca_model.py
caracteristica_id = db.Column(db.BigInteger, db.ForeignKey('caracteristicas.id'))
caracteristica = db.relationship('Caracteristica', backref='marcas')
```
Al crear nuevas entidades similares, seguir este patrón de composición.

### Patrón Persona-Cliente
Separación de datos de persona y rol de cliente:
- `Persona`: datos base (razon_social, direccion, telefono, documento)
- `Cliente`: referencia a Persona con `persona_id`
- Usar `db.session.flush()` para obtener IDs antes del commit final

## Convenciones de Código

### Blueprints (routes/)
```python
# Patrón estándar para blueprints
from flask import Blueprint, render_template, redirect, url_for, flash, request
from utils.db import db

modulo_bp = Blueprint('modulo', __name__, url_prefix='/modulo')

@modulo_bp.route('/')
def get_items():
    items = Model.query.all()
    return render_template('modulo/items.html', items=items)
```

### Formularios (forms.py)
- Todos los formularios WTForms se definen en `forms.py` en la raíz
- Usar `SelectField` con `choices=[]` vacío y poblar dinámicamente en la ruta
- Validaciones personalizadas como métodos `validate_campo(self, field)`

### Templates
- Estructura: `templates/{modulo}/{accion}.html`
- Partials en `_partials/` para componentes reutilizables (ver `templates/ventas/delivery/_partials/`)
- Base template: `templates/base.html` con Bootstrap 5.3.7
- Filtros personalizados registrados en `utils/filters.py`

## Base de Datos

### Configuración
- MySQL local en puerto 3309, base de datos `dbmundo`
- SQLAlchemy como ORM principal
- Migraciones con Alembic (ver `alembic/`)

### Convenciones de Modelos
```python
# Campos estándar en todos los modelos
id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
estado = db.Column(db.SmallInteger, nullable=False, default=1)  # 1=activo
created_at = db.Column(db.DateTime, default=datetime.now)
updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
```

### Transacciones
```python
try:
    db.session.add(objeto)
    db.session.flush()  # Para obtener ID antes de relaciones
    db.session.commit()
except Exception as e:
    db.session.rollback()
    flash(f"Error: {str(e)}", "danger")
```

## Comandos de Desarrollo

```powershell
# Activar entorno virtual
.\env\Scripts\activate

# Ejecutar aplicación
python app.py

# Instalar dependencias
pip install -r requirements.txt

# Exportar dependencias
pip freeze > requirements.txt
```

## Flujo de Delivery (Módulo en Desarrollo Activo)
⚠️ **Estado**: En desarrollo activo - funcionalidades pendientes y corrección de errores en curso.

1. `routes/delivery.py` maneja todo el flujo de pedidos (~500 líneas)
2. Usa `session` de Flask para mantener estado del carrito
3. Renderiza partials dinámicamente para UX fluida (ver `templates/ventas/delivery/_partials/`)
4. Modelo `ProductoVenta` almacena atributos seleccionados como JSON

### Archivos clave del módulo:
- `routes/delivery.py` - Controlador principal
- `templates/ventas/delivery/index.html` - Vista principal
- `templates/ventas/delivery/_partials/` - Componentes: carrito, pedidos, cliente, etc.
- `forms.py` → `DeliveryForm` - Formulario del pedido

## Notas Importantes
- El proyecto usa español para nombres de variables, modelos y rutas
- Campo `estado` en modelos: 1=activo, 0=inactivo (no eliminar registros)
- Archivos estáticos en `static/` (css, js, uploads)
- Imágenes de productos en `static/uploads/images/`
