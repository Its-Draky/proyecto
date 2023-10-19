from flask import Flask, g, render_template, request, redirect, url_for, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'
app.config['UPLOAD_FOLDER'] = 'static/img/uploads'
basedir = os.path.abspath(os.path.dirname(__file__)) 

def get_db():
    sqlite3_database_path = basedir + "/database.db"
    con = sqlite3.connect(sqlite3_database_path)
    con.row_factory = sqlite3.Row
    return con

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Operación List
@app.route('/products/list')
@app.route('/products/list', methods=['GET', 'POST'])
def product_list():
    try:
        with get_db() as con:
            # Obtener la lista de categorías
            categories = con.execute('SELECT id, name FROM categories').fetchall()
            
            selected_category = request.form.get('category')  # Obtener la categoría seleccionada

            if selected_category:
                # Si se selecciona una categoría, filtrar los productos por categoría
                sql = '''
                    SELECT products.*, categories.name AS category_name
                    FROM products
                    LEFT JOIN categories ON products.category_id = categories.id
                    WHERE categories.name = ?
                '''
                res = con.execute(sql, (selected_category,))
                products = res.fetchall()
            else:
                # Si no se selecciona ninguna categoría, mostrar todos los productos
                sql = '''
                    SELECT products.*, categories.name AS category_name
                    FROM products
                    LEFT JOIN categories ON products.category_id = categories.id
                '''
                res = con.execute(sql)
                products = res.fetchall()

            return render_template('products/list.html', products=products, categories=categories, selected_category=selected_category)
    except Exception as e:
        return str(e)
    
@app.route('/products/delete/<int:id>', methods=['GET', 'POST'])
def delete_product(id):
    with get_db() as con:
        res = con.execute('SELECT * FROM products WHERE id = ?', (id,))
        product = res.fetchone()

    if request.method == 'POST':
        with get_db() as con:
            con.execute('DELETE FROM products WHERE id = ?', (id,))
            con.commit()
        return redirect(url_for('product_list'))
    
    return render_template('products/delete.html', product=product)

# Operación Create
@app.route('/products/create', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form['category']  # Obtener el ID de la categoría desde el menú desplegable
        
        photo = request.files['photo']

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            with get_db() as con:
                con.execute('INSERT INTO products (title, description, price, photo, category_id) VALUES (?, ?, ?, ?, ?)', (title, description, price, filename, category_id))
                con.commit()
            return redirect(url_for('product_list'))

    with get_db() as con:
        categories = con.execute('SELECT id, name FROM categories').fetchall()

    return render_template('products/create.html', categories=categories)


# Operación Read
@app.route('/products/read/<int:id>')
def read_product(id):
    with get_db() as con:
        # Realizar una consulta JOIN para obtener el nombre de la categoría
        sql = '''
            SELECT products.*, categories.name AS category_name
            FROM products
            LEFT JOIN categories ON products.category_id = categories.id
            WHERE products.id = ?
        '''
        res = con.execute(sql, (id,))
        product = res.fetchone()
    return render_template('products/read.html', product=product)

# Operación Update
@app.route('/products/update/<int:id>', methods=['GET', 'POST'])
def update_product(id):
    with get_db() as con:
        res = con.execute('SELECT * FROM products WHERE id = ?', (id,))
        product = res.fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category_id = request.form['category']  # Obtener el ID de la categoría desde el menú desplegable

        photo = request.files['photo']

        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            with get_db() as con:
                con.execute('UPDATE products SET title = ?, description = ?, price = ?, photo = ?, category_id = ? WHERE id = ?', (title, description, price, filename, category_id, id))
                con.commit()
            
              # Redirigir a la lista de productos después de actualizar
            return redirect(url_for('product_list'))

    with get_db() as con:
        categories = con.execute('SELECT id, name FROM categories').fetchall()
    
    return render_template('products/update.html', product=product, categories=categories)
    return redirect(url_for('product_list'))



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
