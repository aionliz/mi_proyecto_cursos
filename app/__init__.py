# app/__init__.py

from flask import Flask
from app.config.mysqlconnection import connectToMySQL # Importa la función de conexión

app = Flask(__name__)
app.secret_key = "tu_clave_secreta_aqui" # ¡CAMBIA ESTO POR UNA CLAVE SEGURA!

# Configura la conexión a la base de datos para toda la aplicación
# Puedes acceder a ella en tus modelos con DB = connectToMySQL('nombre_de_tu_db')
# Por ejemplo: DB = connectToMySQL('esquema_estudiantes_cursos')

# Importa y registra tus blueprints (controladores)
from app.controllers import cursos_controller
from app.controllers import estudiantes_controller

# Registra los blueprints
app.register_blueprint(cursos_controller.cursos_bp)
app.register_blueprint(estudiantes_controller.estudiantes_bp)