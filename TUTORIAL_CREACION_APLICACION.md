# 📚 Tutorial: Crear una Aplicación Web de Gestión de Cursos y Estudiantes

**Profesora:** Liza Molina  
**Materia:** Desarrollo Web con Python y Flask  
**Duración estimada:** 8-10 horas  
**Nivel:** Intermedio

## 🎯 Objetivos de Aprendizaje

Al finalizar este tutorial, los estudiantes serán capaces de:

- Crear una aplicación web completa usando Flask
- Implementar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
- Conectar una aplicación Python con MySQL
- Diseñar interfaces web responsivas con Bootstrap
- Aplicar validaciones de datos
- Implementar un sistema de mensajes flash
- Organizar código usando el patrón MVC

## 📋 Prerrequisitos

### Conocimientos previos:

- Python básico e intermedio
- HTML y CSS básico
- Conceptos de bases de datos relacionales
- Terminal/línea de comandos básica

### Software necesario:

- Python 3.8 o superior
- MySQL Server
- Visual Studio Code (recomendado)
- Navegador web moderno

---

## 🚀 FASE 1: Configuración del Entorno

### Paso 1.1: Crear el directorio del proyecto

```bash
mkdir mi_proyecto_cursos
cd mi_proyecto_cursos
```

### Paso 1.2: Crear entorno virtual

```bash
# En Windows
python -m venv venv-todo
venv-todo\Scripts\activate

# En Mac/Linux
python3 -m venv venv-todo
source venv-todo/bin/activate
```

### Paso 1.3: Instalar dependencias

```bash
pip install flask
pip install pymysql
pip install flask-bcrypt
```

### Paso 1.4: Crear estructura de carpetas

```
mi_proyecto_cursos/
├── server.py
├── app/
│   ├── __init__.py
│   ├── config/
│   │   └── mysqlconnection.py
│   ├── controllers/
│   │   ├── cursos_controller.py
│   │   └── estudiantes_controller.py
│   ├── models/
│   │   ├── curso.py
│   │   └── estudiante.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   └── templates/
│       ├── base.html
│       ├── cursos.html
│       ├── editar_curso.html
│       ├── editar_estudiante.html
│       ├── mostrar_curso.html
│       ├── nuevo_estudiante.html
│       └── includes/
│           └── messages.html
└── venv-todo/
```

---

## 🗄️ FASE 2: Configuración de la Base de Datos

### Paso 2.1: Crear la base de datos

```sql
CREATE DATABASE esquema_estudiantes_cursos;
-- Selecciona la base de datos que acabas de crear
USE esquema_estudiantes_cursos;

-- Tabla de Cursos
CREATE TABLE cursos (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de Estudiantes
CREATE TABLE estudiantes (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    curso_id INT NOT NULL, -- Clave foránea para relacionar con la tabla de cursos
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (curso_id) REFERENCES cursos(id) ON DELETE CASCADE ON UPDATE CASCADE
);
```

### Paso 2.2: Configurar conexión a MySQL

**Archivo:** `app/config/mysqlconnection.py`

```python
import pymysql.cursors

class MySQLConnection:
    def __init__(self, db):
        self.connection = pymysql.connect(
            host='localhost',
            user='root',  # Cambiar por tu usuario
            password='root',  # Cambiar por tu contraseña
            db=db,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

    def query_db(self, query, data=None):
        with self.connection.cursor() as cursor:
            try:
                query = cursor.mogrify(query, data)
                print("Ejecutando query:", query)
                cursor.execute(query, data)
                if query.lower().find("insert") >= 0:
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
            except Exception as e:
                print("Error en query_db:", e)
                return False

def connectToMySQL(db):
    return MySQLConnection(db)
```

---

## 📊 FASE 3: Crear los Modelos

### Paso 3.1: Modelo de Curso

**Archivo:** `app/models/curso.py`

```python
# app/models/curso.py

from app.config.mysqlconnection import connectToMySQL
from flask import flash

# Nombre de tu base de datos (¡asegúrate de que coincida con la que creaste!)
DB_NAME = 'esquema_estudiantes_cursos'

class Curso:
    def __init__(self, data):
        self.id = data['id']
        self.nombre = data['nombre']
        self.descripcion = data['descripcion']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.estudiantes = [] # Para almacenar los estudiantes asociados a este curso

    # @classmethod: Este decorador permite que el método sea llamado en la clase (Curso.get_all())
    # sin necesidad de crear una instancia. Recibe 'cls' como primer parámetro (la clase misma).
    # Se usa para operaciones que crean nuevas instancias o trabajan con la clase en general.
    @classmethod
    def get_all(cls):
        # QUERY EXPLICADA: Esta query selecciona todas las columnas (*) de la tabla 'cursos'
        # ORDER BY nombre ASC ordena los resultados alfabéticamente por el campo 'nombre'
        # ASC significa ascendente (A-Z), también podrías usar DESC para descendente (Z-A)
        query = "SELECT * FROM cursos ORDER BY nombre ASC;"
        results = connectToMySQL(DB_NAME).query_db(query)
        cursos = []
        if results:
            for curso_data in results:
                cursos.append(cls(curso_data))
        return cursos

    # @classmethod: Método de clase para guardar un nuevo curso en la base de datos.
    # Al usar 'cls', podemos acceder a la clase sin necesidad de instanciarla primero.
    @classmethod
    def save(cls, data):
        # QUERY EXPLICADA: INSERT INTO agrega un nuevo registro a la tabla 'cursos'
        # Especificamos las columnas (nombre, descripcion) y sus valores
        # %(nombre)s y %(descripcion)s son placeholders que PyMySQL reemplazará con los datos reales
        # Esto previene inyección SQL y es más seguro que concatenar strings
        query = "INSERT INTO cursos (nombre, descripcion) VALUES (%(nombre)s, %(descripcion)s);"
        result = connectToMySQL(DB_NAME).query_db(query, data)
        return result # Devuelve el ID del nuevo curso

    # @classmethod: Método complejo que obtiene un curso con sus estudiantes relacionados.
    # Utiliza JOIN para traer datos de ambas tablas y construye el objeto curso con estudiantes.
    @classmethod
    def get_one_with_estudiantes(cls, curso_id):
        # QUERY COMPLEJA EXPLICADA:
        # Esta query combina datos de dos tablas usando LEFT JOIN
        #
        # SELECT c.*, e.id AS estudiante_id, ...
        # - c.* selecciona todas las columnas de la tabla cursos (alias 'c')
        # - e.id AS estudiante_id renombra la columna 'id' de estudiantes para evitar conflictos
        #
        # FROM cursos c
        # - Establece 'cursos' como tabla principal con alias 'c'
        #
        # LEFT JOIN estudiantes e ON c.id = e.curso_id
        # - LEFT JOIN trae TODOS los cursos, incluso si no tienen estudiantes
        # - INNER JOIN solo traería cursos que SÍ tienen estudiantes
        # - ON c.id = e.curso_id es la condición de unión (clave foránea)
        #
        # WHERE c.id = %(id)s
        # - Filtra para obtener solo el curso específico que buscamos
        query = """
            SELECT c.*, e.id AS estudiante_id, e.nombre AS estudiante_nombre,
                   e.apellido AS estudiante_apellido, e.email AS estudiante_email
            FROM cursos c
            LEFT JOIN estudiantes e ON c.id = e.curso_id
            WHERE c.id = %(id)s;
        """
        data = {'id': curso_id}
        results = connectToMySQL(DB_NAME).query_db(query, data)

        if not results:
            return None

        # Crea la instancia del curso una sola vez
        curso = cls(results[0]) # Usamos el primer resultado para los datos del curso

        # Agrega los estudiantes al curso
        for row in results:
            if row['estudiante_id']: # Solo si hay un estudiante
                estudiante_data = {
                    'id': row['estudiante_id'],
                    'nombre': row['estudiante_nombre'],
                    'apellido': row['estudiante_apellido'],
                    'email': row['estudiante_email'],
                    'curso_id': row['id'], # El ID del curso al que pertenece
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                }
                # Importamos aquí para evitar importación circular
                from app.models.estudiante import Estudiante
                curso.estudiantes.append(Estudiante(estudiante_data))

        return curso

    # @classmethod: Método de clase para actualizar un curso existente.
    # Utiliza 'cls' para mantener la consistencia del patrón de la clase.
    @classmethod
    def update(cls, data):
        # QUERY EXPLICADA: UPDATE modifica registros existentes en la tabla
        # SET especifica qué columnas cambiar y sus nuevos valores
        # WHERE es CRUCIAL - sin él, se actualizarían TODOS los registros
        # %(id)s, %(nombre)s, %(descripcion)s son placeholders seguros
        # NOW() actualiza automáticamente el timestamp
        query = "UPDATE cursos SET nombre=%(nombre)s, descripcion=%(descripcion)s, updated_at=NOW() WHERE id=%(id)s;"
        return connectToMySQL(DB_NAME).query_db(query, data)

    # @classmethod: Método de clase para eliminar un curso y manejar las relaciones.
    # Usa 'cls' para mantener consistencia con el patrón de métodos de la clase.
    @classmethod
    def delete(cls, curso_id):
        # QUERY DELETE DIRECTA EXPLICADA:
        # En el proyecto real, eliminamos directamente el curso
        # Las claves foráneas ON DELETE CASCADE se encargan de las relaciones
        # DELETE FROM elimina registros de la tabla
        # WHERE id = %(id)s especifica exactamente cuál registro eliminar
        query = "DELETE FROM cursos WHERE id = %(id)s;"
        data = {'id': curso_id}
        result = connectToMySQL(DB_NAME).query_db(query, data)
        return result

    # @staticmethod: Este decorador se usa para métodos que NO necesitan acceso a la clase (cls)
    # ni a la instancia (self). Son funciones independientes que están en la clase por organización.
    # Se llaman con Curso.validate_curso() y no requieren instanciar la clase.
    @staticmethod
    def validate_curso(curso):
        is_valid = True
        if len(curso['nombre']) < 3:
            flash("El nombre del curso debe tener al menos 3 caracteres.", "curso_error")
            is_valid = False
        return is_valid
```

### Paso 3.2: Modelo de Estudiante

**Archivo:** `app/models/estudiante.py`

```python
# app/models/estudiante.py

from app.config.mysqlconnection import connectToMySQL
from flask import flash
import re # Para validación de email

# Nombre de tu base de datos
DB_NAME = 'esquema_estudiantes_cursos'

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class Estudiante:
    def __init__(self, data):
        self.id = data['id']
        self.nombre = data['nombre']
        self.apellido = data['apellido']
        self.email = data['email']
        self.curso_id = data['curso_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

    # @classmethod: Método de clase para guardar un nuevo estudiante en la base de datos.
    # Usa 'cls' para acceder a la clase sin necesidad de crear una instancia primero.
    @classmethod
    def save(cls, data):
        # QUERY EXPLICADA: INSERT para crear un nuevo estudiante
        # Insertamos en 4 columnas específicas de la tabla 'estudiantes'
        # Los VALUES corresponden uno a uno con las columnas especificadas
        # %(nombre)s, %(apellido)s, etc. son placeholders que previenen inyección SQL
        query = "INSERT INTO estudiantes (nombre, apellido, email, curso_id) VALUES (%(nombre)s, %(apellido)s, %(email)s, %(curso_id)s);"
        result = connectToMySQL(DB_NAME).query_db(query, data)
        return result

    # @classmethod: Busca un estudiante específico por su ID.
    # Retorna una instancia de la clase o None si no se encuentra.
    @classmethod
    def get_one(cls, estudiante_id):
        # QUERY DE BÚSQUEDA POR ID EXPLICADA:
        # WHERE id = %(id)s busca un estudiante específico por su ID único
        # Esta query debería retornar máximo 1 resultado (ID es único)
        query = "SELECT * FROM estudiantes WHERE id = %(id)s;"
        data = {'id': estudiante_id}
        result = connectToMySQL(DB_NAME).query_db(query, data)
        if result:
            return cls(result[0])
        return None

    # @classmethod: Actualiza la información de un estudiante existente.
    # Usa 'cls' para mantener consistencia con los otros métodos de la clase.
    @classmethod
    def update(cls, data):
        # QUERY UPDATE COMPLETA EXPLICADA:
        # SET actualiza múltiples columnas separadas por comas
        # Cada columna = %(placeholder)s especifica el nuevo valor
        # WHERE id = %(id)s identifica exactamente cuál estudiante modificar
        # NOW() actualiza automáticamente el timestamp
        # Sin WHERE, se actualizarían TODOS los estudiantes (¡peligroso!)
        query = "UPDATE estudiantes SET nombre=%(nombre)s, apellido=%(apellido)s, email=%(email)s, curso_id=%(curso_id)s, updated_at=NOW() WHERE id=%(id)s;"
        return connectToMySQL(DB_NAME).query_db(query, data)

    # @classmethod: Elimina un estudiante de la base de datos.
    # Método de clase que no requiere instanciar un objeto estudiante.
    @classmethod
    def delete(cls, estudiante_id):
        # QUERY DELETE SIMPLE EXPLICADA:
        # DELETE FROM estudiantes elimina registros de la tabla estudiantes
        # WHERE id = %(id)s especifica exactamente cuál estudiante eliminar
        # Al eliminar un estudiante, su curso_id simplemente desaparece (no afecta al curso)
        query = "DELETE FROM estudiantes WHERE id=%(id)s;"
        data = {'id': estudiante_id}
        return connectToMySQL(DB_NAME).query_db(query, data)

    # @staticmethod: Método estático para validar datos de estudiante.
    # No necesita acceso a la clase (cls) ni a instancias (self).
    # Es una función utilitaria que pertenece lógicamente a la clase.
    @staticmethod
    def validate_estudiante(estudiante):
        is_valid = True

        if len(estudiante['nombre']) < 2:
            flash("El nombre del estudiante debe tener al menos 2 caracteres.", "estudiante_error")
            is_valid = False

        if len(estudiante['apellido']) < 2:
            flash("El apellido del estudiante debe tener al menos 2 caracteres.", "estudiante_error")
            is_valid = False

        if not EMAIL_REGEX.match(estudiante['email']):
            flash("Email inválido.", "estudiante_error")
            is_valid = False

        # VALIDACIÓN ÚNICA DE EMAIL EXPLICADA:
        # Esta query verifica si el email ya existe en la base de datos
        # Permite editar un estudiante sin error si el email no cambia
        query = "SELECT * FROM estudiantes WHERE email = %(email)s;"
        data = {'email': estudiante['email']}
        result = connectToMySQL(DB_NAME).query_db(query, data)
        if result and result[0]['id'] != int(estudiante['id']):
            flash("El email ya está registrado.", "estudiante_error")
            is_valid = False

        if not estudiante['curso_id']:
            flash("Debe seleccionar un curso para el estudiante.", "estudiante_error")
            is_valid = False

        return is_valid
```

---

## 🎮 FASE 4: Crear los Controladores

### Paso 4.1: Controlador de Cursos

**Archivo:** `app/controllers/cursos_controller.py`

```python
# app/controllers/cursos_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.curso import Curso

cursos_bp = Blueprint('cursos', __name__)

# Ruta para mostrar todos los cursos y el formulario de creación
@cursos_bp.route('/')
@cursos_bp.route('/cursos')
def index():
    cursos = Curso.get_all()
    return render_template('cursos.html', cursos=cursos)

# Ruta para procesar la creación de un nuevo curso
@cursos_bp.route('/cursos/new', methods=['POST'])
def create_curso():
    if not Curso.validate_curso(request.form):
        return redirect(url_for('cursos.index'))

    data = {
        'nombre': request.form['nombre'],
        'descripcion': request.form['descripcion']
    }
    Curso.save(data)
    flash("Curso creado con éxito!", "success")
    return redirect(url_for('cursos.index'))

# Ruta para mostrar un curso específico y sus estudiantes
@cursos_bp.route('/cursos/<int:curso_id>')
def show_curso(curso_id):
    curso = Curso.get_one_with_estudiantes(curso_id)
    if not curso:
        flash("Curso no encontrado.", "error")
        return redirect(url_for('cursos.index'))
    return render_template('mostrar_curso.html', curso=curso)

# Ruta para mostrar el formulario de edición de un curso
@cursos_bp.route('/cursos/<int:curso_id>/edit')
def edit_curso(curso_id):
    curso = Curso.get_one_with_estudiantes(curso_id)
    if not curso:
        flash("Curso no encontrado para editar.", "error")
        return redirect(url_for('cursos.index'))
    return render_template('editar_curso.html', curso=curso)

# Ruta para procesar la actualización de un curso
@cursos_bp.route('/cursos/<int:curso_id>/update', methods=['POST'])
def update_curso(curso_id):
    if not Curso.validate_curso(request.form):
        return redirect(url_for('cursos.edit_curso', curso_id=curso_id))

    data = {
        'id': curso_id,
        'nombre': request.form['nombre'],
        'descripcion': request.form['descripcion']
    }
    Curso.update(data)
    flash("Curso actualizado con éxito!", "success")
    return redirect(url_for('cursos.show_curso', curso_id=curso_id))

# Ruta para eliminar un curso
@cursos_bp.route('/cursos/<int:curso_id>/delete', methods=['POST'])
def delete_curso(curso_id):
    if Curso.delete(curso_id):
        flash("Curso eliminado con éxito!", "success")
    else:
        flash("Error al eliminar el curso.", "error")
    return redirect(url_for('cursos.index'))
```

### Paso 4.2: Controlador de Estudiantes

**Archivo:** `app/controllers/estudiantes_controller.py`

```python
# app/controllers/estudiantes_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.estudiante import Estudiante
from app.models.curso import Curso # Necesitamos el modelo Curso para el dropdown

estudiantes_bp = Blueprint('estudiantes', __name__)

# Ruta para mostrar el formulario de nuevo estudiante
@estudiantes_bp.route('/estudiantes/new')
def new_estudiante():
    cursos = Curso.get_all() # Obtiene todos los cursos para el dropdown
    return render_template('nuevo_estudiante.html', cursos=cursos)

# Ruta para procesar la creación de un nuevo estudiante
@estudiantes_bp.route('/estudiantes/create', methods=['POST'])
def create_estudiante():
    # El ID del estudiante es 0 para la validación inicial de email único
    form_data = request.form.to_dict()
    form_data['id'] = 0 # Temporal para la validación de email en creación

    if not Estudiante.validate_estudiante(form_data):
        cursos = Curso.get_all() # Vuelve a cargar los cursos si la validación falla
        return render_template('nuevo_estudiante.html', cursos=cursos, form_data=request.form)

    Estudiante.save(request.form)
    flash("Estudiante creado con éxito!", "success")
    return redirect(url_for('cursos.index')) # Redirige a la página de Cursos

# Ruta para mostrar el formulario de edición de un estudiante
@estudiantes_bp.route('/estudiantes/<int:estudiante_id>/edit')
def edit_estudiante(estudiante_id):
    estudiante = Estudiante.get_one(estudiante_id)
    if not estudiante:
        flash("Estudiante no encontrado para editar.", "error")
        return redirect(url_for('cursos.index'))
    cursos = Curso.get_all() # Necesitamos los cursos para el dropdown
    return render_template('editar_estudiante.html', estudiante=estudiante, cursos=cursos)

# Ruta para procesar la actualización de un estudiante
@estudiantes_bp.route('/estudiantes/<int:estudiante_id>/update', methods=['POST'])
def update_estudiante(estudiante_id):
    form_data = request.form.to_dict()
    form_data['id'] = estudiante_id # Asegura que el ID del estudiante esté en los datos

    if not Estudiante.validate_estudiante(form_data):
        cursos = Curso.get_all()
        estudiante = Estudiante.get_one(estudiante_id) # Vuelve a cargar el estudiante
        return render_template('editar_estudiante.html', estudiante=estudiante, cursos=cursos, form_data=request.form)

    data = {
        'id': estudiante_id,
        'nombre': request.form['nombre'],
        'apellido': request.form['apellido'],
        'email': request.form['email'],
        'curso_id': request.form['curso_id']
    }
    Estudiante.update(data)
    flash("Estudiante actualizado con éxito!", "success")
    return redirect(url_for('cursos.show_curso', curso_id=request.form['curso_id']))

# Ruta para eliminar un estudiante
@estudiantes_bp.route('/estudiantes/<int:estudiante_id>/delete', methods=['POST'])
def delete_estudiante(estudiante_id):
    estudiante = Estudiante.get_one(estudiante_id)
    if not estudiante:
        flash("Estudiante no encontrado.", "error")
        return redirect(url_for('cursos.index'))

    curso_id_redireccion = estudiante.curso_id # Guarda el ID del curso antes de eliminar

    if Estudiante.delete(estudiante_id):
        flash("Estudiante eliminado con éxito!", "success")
    else:
        flash("Error al eliminar el estudiante.", "error")

    # Redirige al curso del que fue eliminado, o al índice si no tenía curso
    if curso_id_redireccion:
        return redirect(url_for('cursos.show_curso', curso_id=curso_id_redireccion))
    else:
        return redirect(url_for('cursos.index'))
```

---

## 🎨 FASE 5: Crear las Plantillas HTML

### Paso 5.1: Plantilla Base

**Archivo:** `app/templates/base.html`

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>
      {% block title %}Gestión de Cursos y Estudiantes{% endblock %}
    </title>
    <link
      rel="stylesheet"
      href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
    />
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='css/style.css') }}?v=2"
    />
  </head>
  <body>
    <nav class="navbar navbar-expand-lg custom-navbar">
      <div class="container">
        <a class="navbar-brand" href="{{ url_for('cursos.index') }}"
          >📚 Gestión Académica</a
        >
        <button
          class="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarNav"
        >
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ml-auto">
            <li class="nav-item">
              <a class="nav-link" href="{{ url_for('cursos.index') }}"
                >📋 Cursos</a
              >
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                href="{{ url_for('estudiantes.new_estudiante') }}"
                >👨‍🎓 Nuevo Estudiante</a
              >
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container main-content">
      {% with messages = get_flashed_messages(with_categories=true) %} {% if
      messages %}
      <div class="flash-messages-container">
        {% for category, message in messages %}
        <div class="flash-message flash-{{ category }}">{{ message }}</div>
        {% endfor %}
      </div>
      {% endif %} {% endwith %} {% block content %}{% endblock %}
    </div>

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
  </body>
</html>
```

### Paso 5.2: Página Principal de Cursos

**Archivo:** `app/templates/cursos.html`

```html
{% extends "base.html" %} {% block title %}Cursos{% endblock %} {% block content
%}
<div class="row">
  <div class="col-md-6">
    <h2>Crear Nuevo Curso</h2>
    <form action="{{ url_for('cursos.create_curso') }}" method="POST">
      <div class="form-group">
        <label for="nombre">Nombre del Curso:</label>
        <input
          type="text"
          class="form-control"
          id="nombre"
          name="nombre"
          required
        />
      </div>
      <div class="form-group">
        <label for="descripcion">Descripción:</label>
        <textarea
          class="form-control"
          id="descripcion"
          name="descripcion"
          rows="3"
        ></textarea>
      </div>
      <button type="submit" class="btn btn-primary">Crear Curso</button>
    </form>
  </div>
  <div class="col-md-6">
    <h2>Cursos Existentes</h2>
    {% if cursos %}
    <ul class="list-group">
      {% for curso in cursos %}
      <li
        class="list-group-item d-flex justify-content-between align-items-center"
      >
        <a href="{{ url_for('cursos.show_curso', curso_id=curso.id) }}"
          >{{ curso.nombre }}</a
        >
        <div>
          <a
            href="{{ url_for('cursos.edit_curso', curso_id=curso.id) }}"
            class="btn btn-warning btn-sm mr-2"
            >Editar</a
          >
          <form
            action="{{ url_for('cursos.delete_curso', curso_id=curso.id) }}"
            method="POST"
            style="display:inline;"
          >
            <button
              type="submit"
              class="btn btn-danger btn-sm"
              onclick="return confirm('¿Estás seguro?')"
            >
              Eliminar
            </button>
          </form>
        </div>
      </li>
      {% endfor %}
    </ul>
    {% else %}
    <p>No hay cursos registrados aún.</p>
    {% endif %}
  </div>
</div>
{% endblock %}
```

### Paso 5.3: Formulario de Nuevo Estudiante

**Archivo:** `app/templates/nuevo_estudiante.html`

```html
{% extends "base.html" %}

{% block title %}Nuevo Estudiante{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8 offset-md-2">
        <h2>Registrar Nuevo Estudiante</h2>
        <form action="{{ url_for('estudiantes.create_estudiante') }}" method="POST">
            <div class="form-group">
                <label for="nombre">Nombre:</label>
                <input type="text" class="form-control" id="nombre" name="nombre" value="{{ form_data.nombre if form_data else '' }}" required>
            </div>
            <div class="form-group">
                <label for="apellido">Apellido:</label>
                <input type="text" class="form-control" id="apellido" name="apellido" value="{{ form_data.apellido if form_data else '' }}" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" class="form-control" id="email" name="email" value="{{ form_data.email if form_data else '' }}" required>
            </div>
            <div class="form-group">
                <label for="curso_id">Curso:</label>
                <select class="form-control" id="curso_id" name="curso_id" required>
                    <option value="">-- Selecciona un Curso --</option>
                    {% for curso in cursos %}
                    <option value="{{ curso.id }}" {% if form_data and form_data.curso_id|int == curso.id %}selected{% endif %}>{{ curso.nombre }}</option>
                    {% endfor %}
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Registrar Estudiante</button>
            <a href="{{ url_for('cursos.index') }}" class="btn btn-secondary">Cancelar</a>
        </form>
    </div>
</div>
{% endblock %}
```

---

## 🎨 FASE 6: Estilos CSS Personalizados

### Paso 6.1: Crear archivo de estilos

**Archivo:** `app/static/css/style.css`

```css
/* Estilos base del body y contenedores */
body {
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  background-color: #1a1a1a;
  color: #cccccc;
  padding-top: 0;
}

/* Barra de navegación personalizada */
.custom-navbar {
  background: #3a3a3a;
  padding: 10px 0;
  margin-bottom: 40px;
  width: 100%;
  z-index: 1030;
  border-radius: 0;
}

/* Logo/marca de la navbar */
.custom-navbar .navbar-brand {
  font-weight: bold;
  font-size: 1.6rem;
  color: #b19cd9;
  text-decoration: none;
  transition: all 0.3s ease;
}

/* Enlaces de navegación */
.custom-navbar .nav-link {
  color: #f0f0f0;
  font-weight: 500;
  padding: 10px 18px;
  border-radius: 0;
  transition: all 0.3s ease;
  margin: 0 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Hover de enlaces de navegación */
.custom-navbar .nav-link:hover {
  background-color: rgba(177, 156, 217, 0.2);
  color: #ffffff;
  border-radius: 15px;
}

/* Tarjetas de contenido */
.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
  margin-bottom: 30px;
  background-color: #2d2d2d;
  color: #f0f0f0;
}

/* Encabezado de tarjetas */
.card-header {
  background-color: #c8aae6;
  color: #3a3a3a;
  font-size: 1.35rem;
  font-weight: 600;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
  padding: 1.2rem 1.5rem;
}

/* Botones con tonalidades pastel medias */
.btn-primary {
  background-color: #b8d4f1;
  border-color: #b8d4f1;
  color: #4a90e2;
}

.btn-success {
  background-color: #b8e6b8;
  border-color: #b8e6b8;
  color: #4caf50;
}

.btn-warning {
  background-color: #f5d56b;
  border-color: #f5d56b;
  color: #b8860b;
}

.btn-danger {
  background-color: #f5a3a3;
  border-color: #f5a3a3;
  color: #c62828;
}

/* Campos de formulario */
.form-control {
  background-color: #1a1a1a;
  color: #f0f0f0;
  border-radius: 8px;
  border: 1px solid #6c757d;
  padding: 0.85rem 1.1rem;
}

/* Mensajes flash */
.flash-message {
  padding: 18px 25px;
  margin-bottom: 18px;
  border-radius: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1.05rem;
}

.flash-success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.flash-error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
```

---

## 🔧 FASE 7: Configuración Principal

### Paso 7.1: Archivo principal del servidor

**Archivo:** `server.py`

```python
# server.py

from app import app
from app.controllers import cursos_controller, estudiantes_controller # Importa tus controladores

if __name__ == "__main__":
    app.run(debug=True) # debug=True para desarrollo, ¡cámbialo a False en producción!
```

### Paso 7.2: Archivo **init**.py

**Archivo:** `app/__init__.py`

```python
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
```

---

## 🚀 FASE 8: Ejecutar la Aplicación

### Paso 8.1: Activar entorno virtual

```bash
# En Windows
venv-todo\Scripts\activate

# En Mac/Linux
source venv-todo/bin/activate
```

### Paso 8.2: Ejecutar el servidor

```bash
python server.py
```

### Paso 8.3: Acceder a la aplicación

Abrir navegador en: `http://localhost:5000`

---

## 🧪 FASE 9: Pruebas y Validación

### Pruebas funcionales a realizar:

1. **Gestión de Cursos:**

   - ✅ Crear un nuevo curso
   - ✅ Listar todos los cursos
   - ✅ Ver detalles de un curso
   - ✅ Editar información del curso
   - ✅ Eliminar un curso

2. **Gestión de Estudiantes:**

   - ✅ Registrar nuevo estudiante
   - ✅ Asignar estudiante a curso
   - ✅ Editar información del estudiante
   - ✅ Eliminar estudiante

3. **Validaciones:**

   - ✅ Campos obligatorios
   - ✅ Formato de email válido
   - ✅ Longitud mínima de nombres

4. **Interfaz:**
   - ✅ Responsive design
   - ✅ Mensajes de feedback
   - ✅ Navegación intuitiva

---

## 📚 Conceptos Técnicos Explicados

### 1. **Patrón MVC (Modelo-Vista-Controlador):**

- **Modelos:** Manejan la lógica de datos y base de datos
- **Vistas:** Plantillas HTML que muestran la información
- **Controladores:** Manejan las rutas y lógica de negocio

### 2. **Blueprints en Flask:**

- **¿Qué son?** Manera de organizar rutas en módulos separados
- **Ventajas:** Código más limpio, reutilizable y mantenible
- **Registro:** Se registran en `app/__init__.py` con `app.register_blueprint()`
- **Uso:** Cada controlador es un Blueprint independiente

### 3. **ORM Personalizado:**

- Métodos de clase para operaciones CRUD
- Validaciones en el modelo
- Relaciones entre tablas con JOIN queries

### 4. **Decoradores @classmethod y @staticmethod:**

#### **@classmethod:**

- **Propósito:** Métodos que pertenecen a la clase, no a instancias específicas
- **Parámetro:** Recibe `cls` como primer parámetro (referencia a la clase)
- **Uso:** Operaciones CRUD, factory methods, métodos que crean instancias
- **Ejemplo:** `Curso.get_all()` - obtiene todos los cursos sin necesidad de instanciar
- **Ventaja:** Acceso a la clase para crear nuevas instancias del tipo correcto

#### **@staticmethod:**

- **Propósito:** Funciones que pertenecen lógicamente a la clase pero no necesitan acceso a ella
- **Parámetros:** No recibe `self` ni `cls` automáticamente
- **Uso:** Validaciones, utilidades, funciones de ayuda
- **Ejemplo:** `Curso.validate_curso()` - valida datos sin necesitar la clase
- **Ventaja:** Organización del código y namespace limpio

#### **¿Cuándo usar cada uno?**

- **@classmethod:** Cuando necesitas crear instancias o acceder a atributos de clase
- **@staticmethod:** Cuando la función está relacionada con la clase pero es independiente

### 5. **Queries SQL Explicadas:**

#### **SELECT - Consultar Datos:**

```sql
-- Básico: Seleccionar todas las columnas
SELECT * FROM cursos;

-- Con ordenamiento
SELECT * FROM cursos ORDER BY nombre ASC;

-- Con filtros específicos
SELECT * FROM cursos WHERE id = 1;
```

#### **INSERT - Insertar Datos:**

```sql
-- Insertar nuevo registro especificando columnas
INSERT INTO cursos (nombre, descripcion)
VALUES ('Python Avanzado', 'Curso de programación');

-- Los placeholders %(nombre)s previenen inyección SQL
```

#### **UPDATE - Actualizar Datos:**

```sql
-- Actualizar campos específicos
UPDATE cursos
SET nombre = 'Nuevo Nombre', descripcion = 'Nueva descripción'
WHERE id = 1;

-- ¡IMPORTANTE! Siempre usar WHERE para evitar actualizar todos los registros
```

#### **DELETE - Eliminar Datos:**

```sql
-- Eliminar registro específico
DELETE FROM cursos WHERE id = 1;

-- ¡CUIDADO! Sin WHERE eliminarías TODOS los registros
```

#### **JOIN - Combinar Tablas:**

```sql
-- LEFT JOIN: Trae todos los registros de la tabla izquierda
SELECT c.*, e.nombre as estudiante_nombre
FROM cursos c
LEFT JOIN estudiantes e ON c.id = e.curso_id;

-- INNER JOIN: Solo registros que coinciden en ambas tablas
SELECT c.*, e.nombre
FROM cursos c
INNER JOIN estudiantes e ON c.id = e.curso_id;
```

#### **Placeholders Seguros:**

- **%(nombre)s**: PyMySQL reemplaza automáticamente
- **Previene inyección SQL**: Nunca concatenes strings directamente
- **Ejemplo seguro**: `WHERE id = %(id)s`
- **Ejemplo PELIGROSO**: `WHERE id = " + str(id) + "` ❌

### 6. **Sistema de Templating Jinja2:**

- Herencia de plantillas con `extends`
- Bloques de contenido con `block`
- Variables y estructuras de control
- URL generation con `url_for()`

### 7. **Responsive Design:**

- Bootstrap para componentes
- CSS Grid para layouts
- CSS personalizado para temas

---

## 🔍 Ejercicios Adicionales

### Nivel Básico:

1. Agregar campo "fecha de nacimiento" a estudiantes
2. Implementar búsqueda de cursos por nombre
3. Agregar contador de estudiantes por curso

### Nivel Intermedio:

1. Sistema de autenticación de usuarios
2. Subida de fotos de estudiantes
3. Exportar lista de estudiantes a CSV

### Nivel Avanzado:

1. API REST con endpoints JSON
2. Sistema de calificaciones
3. Dashboard con gráficos estadísticos

---

## 🐛 Troubleshooting Común

### Error: "No module named 'pymysql'"

**Solución:** `pip install pymysql`

### Error: "Access denied for user"

**Solución:** Verificar credenciales en `mysqlconnection.py`

### Error: "Table doesn't exist"

**Solución:** Ejecutar scripts SQL de creación de tablas

### Error: "Template not found"

**Solución:** Verificar estructura de carpetas y nombres de archivos

---

## 📖 Recursos Adicionales

### Documentación oficial:

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [Bootstrap Documentation](https://getbootstrap.com/)

### Herramientas recomendadas:

- **Visual Studio Code:** Editor principal
- **MySQL Workbench:** Gestión de base de datos
- **Postman:** Pruebas de API (futuras)

---

## 🎯 Criterios de Evaluación

### Funcionalidad (40%):

- Todas las operaciones CRUD funcionan correctamente
- Validaciones implementadas adecuadamente
- Navegación fluida entre páginas

### Código (30%):

- Estructura organizacional clara
- Comentarios y documentación
- Buenas prácticas de programación

### Interfaz (20%):

- Diseño responsive
- Usabilidad intuitiva
- Estética profesional

### Creatividad (10%):

- Funcionalidades adicionales
- Mejoras en el diseño
- Optimizaciones de rendimiento

---

## 🎊 ¡Felicitaciones!

Has completado exitosamente la creación de una aplicación web completa con Flask. Este proyecto te ha permitido aprender:

- ✅ Desarrollo web full-stack con Python
- ✅ Gestión de bases de datos relacionales
- ✅ Diseño de interfaces responsivas
- ✅ Implementación del patrón MVC
- ✅ Validaciones y manejo de errores
- ✅ Organización de código en proyectos grandes

**¡Continúa practicando y construyendo proyectos más complejos!**

---

_Desarrollado por: [Tu nombre] - Profesora de Informática_
_Fecha de creación: Agosto 2025_
_Versión: 1.0_

```

```
