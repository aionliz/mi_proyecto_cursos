# server.py

from app import app
from app.controllers import cursos_controller, estudiantes_controller # Importa tus controladores

if __name__ == "__main__":
    app.run(debug=True) # debug=True para desarrollo, ¡cámbialo a False en producción!