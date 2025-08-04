# app/controllers/cursos_controller.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.curso import Curso

cursos_bp = Blueprint('cursos', __name__)

# Ruta para mostrar todos los cursos y el formulario de creación (Paso 2)
@cursos_bp.route('/')
@cursos_bp.route('/cursos')
def index():
    cursos = Curso.get_all()
    return render_template('cursos.html', cursos=cursos)

# Ruta para procesar la creación de un nuevo curso (Paso 2)
@cursos_bp.route('/cursos/new', methods=['POST'])
def create_curso():
    if not Curso.validate_curso(request.form):
        return redirect(url_for('cursos.index')) # Redirige de vuelta si la validación falla
    
    data = {
        'nombre': request.form['nombre'],
        'descripcion': request.form['descripcion']
    }
    Curso.save(data)
    flash("Curso creado con éxito!", "success")
    return redirect(url_for('cursos.index'))

# Ruta para mostrar un curso específico y sus estudiantes (Paso 3 y 7)
@cursos_bp.route('/cursos/<int:curso_id>')
def show_curso(curso_id):
    curso = Curso.get_one_with_estudiantes(curso_id)
    if not curso:
        flash("Curso no encontrado.", "error")
        return redirect(url_for('cursos.index'))
    return render_template('mostrar_curso.html', curso=curso)

# Ruta para mostrar el formulario de edición de un curso (Paso 9)
@cursos_bp.route('/cursos/<int:curso_id>/edit')
def edit_curso(curso_id):
    curso = Curso.get_one_with_estudiantes(curso_id) # Usamos el mismo método para obtener los datos
    if not curso:
        flash("Curso no encontrado para editar.", "error")
        return redirect(url_for('cursos.index'))
    return render_template('editar_curso.html', curso=curso)

# Ruta para procesar la actualización de un curso (Paso 9)
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

# Ruta para eliminar un curso (Paso 9)
@cursos_bp.route('/cursos/<int:curso_id>/delete', methods=['POST'])
def delete_curso(curso_id):
    if Curso.delete(curso_id):
        flash("Curso eliminado con éxito!", "success")
    else:
        flash("Error al eliminar el curso.", "error")
    return redirect(url_for('cursos.index'))