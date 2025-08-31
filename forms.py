from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, IntegerField, DateField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, NumberRange, Optional, length
from flask_wtf.file import FileAllowed


#creamos las clases de cada formulario

class MarcaForm(FlaskForm):
    
    nombre = StringField('Nombre:', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción:', validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
class CategoriaForm(FlaskForm):
    
    nombre = StringField('Nombre:', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción:', validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
class PresentacionForm(FlaskForm):
    
    nombre = StringField('Nombre:', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción:', validators=[DataRequired()])
    submit = SubmitField('Guardar')
    
class ProductoForm(FlaskForm):
    codigo = StringField('Código:', validators=[DataRequired(), length(min=1, max=50)])
    nombre = StringField('Nombre:', validators=[DataRequired(message="El nombre es obligatorio."), length(min=1, max=80)])
    descripcion = TextAreaField('Descripción:', validators=[Optional(strip_whitespace=True), length(max=255)])
    fechaVencimiento = DateField('Fecha de Vencimiento:', format='%Y-%m-%d', validators=[Optional()])
    imagen = FileField('Imagen:', validators=[Optional(), FileAllowed(['jpg', 'png'], 'Solo se permiten imágenes JPG y PNG.')])
    marcas = SelectField('Marca:', choices=[], validators=[DataRequired()])
    presentaciones = SelectField('Presentación:', choices=[], validators=[DataRequired()])
    categorias = SelectMultipleField('Categorías:', choices=[], validators=[DataRequired("Seleccione al menos una categoría.")])
    submit = SubmitField('Guardar')