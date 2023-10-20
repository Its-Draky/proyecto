# routes_main.py
from flask import Blueprint, redirect, render_template, url_for, request
from . import db_manager as db
from . import app
from .models import Product, Category
from werkzeug.utils import secure_filename
import os

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

main_bp = Blueprint(
    "main_bp", __name__, template_folder="templates", static_folder="static"
)

@main_bp.route('/')
def init():
    return redirect(url_for('main_bp.product_list'))

@main_bp.route('/products/list', methods=['GET', 'POST'])
def product_list():
    try:
        categories = Category.query.all()
        selected_category = request.form.get('category')

        if selected_category:
            category = Category.query.filter_by(name=selected_category).first()
            if category:
                products = Product.query.filter_by(category_id=category.id).all()
            else:
                products = []
        else:
            products = Product.query.all()

        return render_template('products/list.html', products=products, categories=categories, selected_category=selected_category)
    except Exception as e:
        return str(e)

@main_bp.route('/products/update/<int:id>', methods=['GET', 'POST'])
def product_update(id):
    product = Product.query.get(id)
    categories = Category.query.all()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category_id = int(request.form['category'])
        new_photo = request.files['photo']

        if new_photo and allowed_file(new_photo.filename):
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], product.photo)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.photo))
            filename = secure_filename(new_photo.filename)
            new_photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            product.title = title
            product.description = description
            product.price = price
            product.category_id = category_id
            product.photo = filename
        else:
            product.title = title
            product.description = description
            product.price = price
            product.category_id = category_id

        db.session.commit()
        return redirect(url_for('main_bp.product_list'))

    return render_template('products/update.html', product=product, categories=categories)

@main_bp.route('/products/create', methods=['GET', 'POST'])
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
            return redirect(url_for('main_bp.product_list'))

    return render_template('products/create.html', categories=categories)

@main_bp.route('/products/read/<int:id>')
def product_read(id):
    product = Product.query.get(id)
    return render_template('products/read.html', product=product)

@main_bp.route('/products/delete/<int:id>', methods=['GET', 'POST'])
def product_delete(id):
    product = Product.query.get(id)

    if request.method == 'POST':
        db.session.delete(product)
        db.session.commit()
        return redirect(url_for('main_bp.product_list'))

    return render_template('products/delete.html', product=product)

if __name__ == '__main__':
    app.run(debug=True)
