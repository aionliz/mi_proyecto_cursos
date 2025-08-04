# app/controllers/estudiantes_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.estudiante import Estudiante
from app.models.curso import Curso # Necesitamos el modelo Curso para el dropdown

estudiantes_bp = Blueprint('estudiantes', __name__)

# Ruta para mostrar el formulario de nuevo estudiante (Paso 4 y 5)
@estudiantes_bp.route('/estudiantes/new')
def new_estudiante():
    cursos = Curso.get_all() # Obtiene todos los cursos para el dropdown
    return render_template('nuevo_estudiante.html', cursos=cursos)

# Ruta para procesar la creación de un nuevo estudiante (Paso 4 y 6)
@estudiantes_bp.route('/estudiantes/create', methods=['POST'])
def create_estudiante():
    # El ID del estudiante es 0 para la validación inicial de email único
    form_data = request.form.to_dict()
    form_data['id'] = 0 # Temporal para la validación de email en creación
    
    if not Estudiante.validate_estudiante(form_data):
        cursos = Curso.get_all() # Vuelve a cargar los cursos si la validación falla
        return render_template('nuevo_estudiante.html', cursos=cursos, form_data=request.form) # Pasa los datos para rellenar el formulario
    
    Estudiante.save(request.form)
    flash("Estudiante creado con éxito!", "success")
    return redirect(url_for('cursos.index')) # Redirige a la página de Cursos (Paso 6)

# Ruta para mostrar el formulario de edición de un estudiante (Paso 9)
@estudiantes_bp.route('/estudiantes/<int:estudiante_id>/edit')
def edit_estudiante(estudiante_id):
    estudiante = Estudiante.get_one(estudiante_id)
    if not estudiante:
        flash("Estudiante no encontrado para editar.", "error")
        return redirect(url_for('cursos.index')) # O a una página de error
    cursos = Curso.get_all() # Necesitamos los cursos para el dropdown
    return render_template('editar_estudiante.html', estudiante=estudiante, cursos=cursos)

# Ruta para procesar la actualización de un estudiante (Paso 9)
@estudiantes_bp.route('/estudiantes/<int:estudiante_id>/update', methods=['POST'])
def update_estudiante(estudiante_id):
    form_data = request.form.to_dict()
    form_data['id'] = estudiante_id # Asegura que el ID del estudiante esté en los datos para la validación
    
    if not Estudiante.validate_estudiante(form_data):
        cursos = Curso.get_all()
        estudiante = Estudiante.get_one(estudiante_id) # Vuelve a cargar el estudiante para el formulario
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
    return redirect(url_for('cursos.show_curso', curso_id=request.form['curso_id'])) # Redirige al curso del estudiante

# Ruta para eliminar un estudiante (Paso 9)
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