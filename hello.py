from flask import Flask, g, render_template
import sqlite3, os

app = Flask(__name__)
app.config['DATABASE'] = 'database.db'

basedir = os.path.abspath(os.path.dirname(__file__)) 
def get_db():
    sqlite3_database_path =  basedir + "/database.db"
    con = sqlite3.connect(sqlite3_database_path)
    # https://docs.python.org/3/library/sqlite3.html#how-to-create-and-use-row-factories
    con.row_factory = sqlite3.Row
    return con

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/products/list')
def product_list():

    try:
        with get_db() as con:
            res = con.execute('SELECT * FROM products')
            products = res.fetchall()
            return render_template('products/list.html', products=products)
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)
