# config/mysqlconnection.py

import pymysql.cursors

class MySQLConnection:
    def __init__(self, db):
        try:
            connection = pymysql.connect(
                host='localhost',
                user='root',
                password='tazmania2316', # ¡IMPORTANTE! Cambia esto por tu contraseña de MySQL
                db=db,# Nombre de la base de datos
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            self.connection = connection
        except pymysql.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            self.connection = None # Establece la conexión a None en caso de error

    def query_db(self, query, data=None):
        if not self.connection:
            print("No hay conexión a la base de datos.")
            return False

        with self.connection.cursor() as cursor:
            try:
                if data:
                    print("Running Query:", cursor.mogrify(query, data))

                cursor.execute(query, data)

                if query.lower().find("insert") >= 0:
                    self.connection.commit()
                    return cursor.lastrowid
                elif query.lower().find("select") >= 0:
                    result = cursor.fetchall()
                    return result
                else:
                    self.connection.commit()
                    return True # Para UPDATE/DELETE, indica éxito
            except Exception as e:
                print(f"Something went wrong with query: {e}")
                return False
            finally:
                pass # No cerramos la conexión aquí

def connectToMySQL(db):
    return MySQLConnection(db)