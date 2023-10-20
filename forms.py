from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, FloatField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired

class CreateProductForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    price = FloatField('Precio', validators=[DataRequired()])
    photo = FileField('Foto', validators=[DataRequired()])
    category = SelectField('Categoria', coerce=int, validators=[DataRequired()])

class UpdateProductForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    price = DecimalField('Precio', validators=[DataRequired()])
    category = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    photo = FileField('Foto del Producto')

class DeleteProductForm(FlaskForm):
    confirm = SubmitField('Eliminar', validators=[DataRequired()])