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

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM cursos ORDER BY nombre ASC;"
        results = connectToMySQL(DB_NAME).query_db(query)
        cursos = []
        if results:
            for curso_data in results:
                cursos.append(cls(curso_data))
        return cursos

    @classmethod
    def save(cls, data):
        query = "INSERT INTO cursos (nombre, descripcion) VALUES (%(nombre)s, %(descripcion)s);"
        result = connectToMySQL(DB_NAME).query_db(query, data)
        return result # Devuelve el ID del nuevo curso

    @classmethod
    def get_one_with_estudiantes(cls, curso_id):
        query = """
            SELECT c.*, e.id AS estudiante_id, e.nombre AS estudiante_nombre, e.apellido AS estudiante_apellido, e.email AS estudiante_email
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

        # Agrega los estudiantes si existen
        for row in results:
            if row['estudiante_id']: # Si hay datos de estudiante
                estudiante_data = {
                    'id': row['estudiante_id'],
                    'nombre': row['estudiante_nombre'],
                    'apellido': row['estudiante_apellido'],
                    'email': row['estudiante_email'],
                    'curso_id': row['id'], # El ID del curso al que pertenece
                    'created_at': row['created_at'], # Estos campos no están en el SELECT del estudiante, se heredarán del curso o se manejarán en el modelo de estudiante
                    'updated_at': row['updated_at']
                }
                # Importa Estudiante aquí para evitar importación circular
                from app.models.estudiante import Estudiante
                curso.estudiantes.append(Estudiante(estudiante_data))
        return curso

    @classmethod
    def update(cls, data):
        query = "UPDATE cursos SET nombre=%(nombre)s, descripcion=%(descripcion)s, updated_at=NOW() WHERE id=%(id)s;"
        return connectToMySQL(DB_NAME).query_db(query, data)

    @classmethod
    def delete(cls, curso_id):
        query = "DELETE FROM cursos WHERE id=%(id)s;"
        data = {'id': curso_id}
        return connectToMySQL(DB_NAME).query_db(query, data)

    @staticmethod
    def validate_curso(curso):
        is_valid = True
        if len(curso['nombre']) < 3:
            flash("El nombre del curso debe tener al menos 3 caracteres.", "curso_error")
            is_valid = False
        return is_valid