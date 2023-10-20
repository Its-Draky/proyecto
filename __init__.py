from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db_manager = SQLAlchemy()

app = Flask(__name__)

app.config["SECRET_KEY"] = "axel"
basedir = os.path.abspath(os.path.dirname(__file__)) 

app.config['UPLOAD_FOLDER'] = 'static/img/uploads'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")
app.logger.debug("SQLITE: "+app.config["SQLALCHEMY_DATABASE_URI"] )
app.config['SQLALCHEMY_ECHO'] = True
db_manager.init_app(app)

with app.app_context():

    from .routes_main import main_bp
    app.register_blueprint(main_bp)


if __name__ == '__main__':
    app.run(debug=True)
