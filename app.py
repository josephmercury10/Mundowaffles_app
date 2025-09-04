from flask import Flask, render_template, jsonify
from flask_mysqldb import MySQL
#from flask_sqlalchemy import SQLAlchemy
from config import config
from utils.db import db

# Importar los blueprints
from routes.marcas import marcas_bp
from routes.caracteristicas import caracteristicas_bp
from routes.categorias import categorias_bp
from routes.presentaciones import presentaciones_bp
from routes.productos import productos_bp
from routes.pos import pos_bp
from routes.clientes import clientes_bp


app = Flask(__name__)

app.config.from_object(config['development'])

conexion = MySQL(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/dbmundo'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# Registrar los blueprints
app.register_blueprint(marcas_bp)
app.register_blueprint(caracteristicas_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(presentaciones_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(pos_bp)
app.register_blueprint(clientes_bp)

#def pagina_no_encontrada(error):
 #   return "<h1>Página no encontrada</h1><p>Lo sentimos, la página que buscas no existe.</p>"



if __name__ == '__main__':
    app.config.from_object(config['development'])
    #app.register_error_handler(404, pagina_no_encontrada)
    app.run()
    
