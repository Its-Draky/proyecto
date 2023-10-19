from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/img/uploads'
# Configuración de la base de datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

# Definición del modelo de la tabla Product
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    photo = db.Column(db.String, nullable=False)
    category = db.relationship('Category', backref='products')

# Definición del modelo de la tabla Category
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# Rutas y vistas
@app.route('/')
def init():
    return redirect(url_for('product_list'))

@app.route('/products/list', methods=['GET', 'POST'])
def product_list():
    try:
        categories = Category.query.all()  # Obtener la lista de categorías

        selected_category = request.form.get('category')  # Obtener la categoría seleccionada

        if selected_category:
            # Buscar la categoría por su nombre
            category = Category.query.filter_by(name=selected_category).first()

            if category:
                # Si se encuentra la categoría, filtrar los productos por su ID
                products = Product.query.filter_by(category_id=category.id).all()
            else:
                # Manejar el caso en el que la categoría no se encuentra
                products = []

        else:
            # Si no se selecciona ninguna categoría, mostrar todos los productos
            products = Product.query.all()

        return render_template('products/list.html', products=products, categories=categories, selected_category=selected_category)
    except Exception as e:
        return str(e)



@app.route('/products/update/<int:id>', methods=['GET', 'POST'])
def product_update(id):
    product = Product.query.get(id)
    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category'])

        # Comprueba si se ha enviado una nueva imagen
        new_photo = request.files['photo']

        if new_photo and allowed_file(new_photo.filename):
            # Borra la imagen anterior si existe
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], product.photo)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.photo))

            # Guarda la nueva imagen
            filename = secure_filename(new_photo.filename)
            new_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # Actualiza la información del producto
            product.title = title
            product.description = description
            product.price = price
            product.category_id = category_id
            product.photo = filename

        else:
            # Si no se proporciona una nueva imagen, simplemente actualiza la información
            product.title = title
            product.description = description
            product.price = price
            product.category_id = category_id

        db.session.commit()

        return redirect(url_for('product_list'))

    return render_template('products/update.html', product=product, categories=categories)


@app.route('/products/create', methods=['GET', 'POST'])
def product_create():
    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category'])

        photo = request.files['photo']

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_product = Product(title=title, description=description, price=price, category_id=category_id, photo=filename)
            db.session.add(new_product)
            db.session.commit()

            return redirect(url_for('product_list'))

    return render_template('products/create.html', categories=categories)

@app.route('/products/read/<int:id>')
def product_read(id):
    product = Product.query.get(id)
    return render_template('products/read.html', product=product)

@app.route('/products/delete/<int:id>', methods=['GET', 'POST'])
def product_delete(id):
    product = Product.query.get(id)

    if request.method == 'POST':
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('product_list'))

    return render_template('products/delete.html', product=product)

if __name__ == '__main__':
    app.run(debug=True)
