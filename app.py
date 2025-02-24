from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# Intentar importar Firebase
try:
    from firebase_config import db
    firebase_disponible = True
except Exception as e:
    print(f"Error al inicializar Firebase: {str(e)}")
    firebase_disponible = False

# Cargar alumnos desde el archivo JSON con manejo de errores
try:
    archivo_json = "alumnos_corregidos.json"
    if not os.path.exists(archivo_json):
        print(f"Error: El archivo {archivo_json} no existe")
        alumnos = []
    else:
        with open(archivo_json, "r", encoding="utf-8") as file:
            alumnos = json.load(file)
except Exception as e:
    print(f"Error al cargar el archivo JSON: {str(e)}")
    alumnos = []

# Ruta de prueba para verificar que la API está activa
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "estado": "activo",
        "firebase_disponible": firebase_disponible,
        "mensaje": "API funcionando correctamente",
        "alumnos_cargados": len(alumnos)
    })

# Ruta para cargar alumnos en Firebase
@app.route('/cargar_alumnos', methods=['POST'])
def cargar_alumnos():
    if not firebase_disponible:
        return jsonify({
            "error": "Firebase no está disponible",
            "estado": "error"
        }), 500

    try:
        if not alumnos:
            return jsonify({
                "error": "No hay alumnos para cargar. Verifica que el archivo JSON existe y tiene el formato correcto.",
                "estado": "error"
            }), 400
            
        alumnos_cargados = 0
        for alumno in alumnos:
            usuario = alumno["usuario"]
            nombre = alumno["nombre"]
            turno = alumno["turno"]
            grupo = alumno["grupo"]
            clave = alumno["clave"]
            saldo_inicial = 100  # Definir saldo inicial

            user_ref = db.collection('usuarios').document(usuario)
            user_ref.set({
                'nombre': nombre,
                'turno': turno,
                'grupo': grupo,
                'clave': clave,
                'saldo': saldo_inicial,
                'transacciones': []
            })
            alumnos_cargados += 1
        
        return jsonify({
            "mensaje": f"Se registraron {alumnos_cargados} alumnos en Firebase con saldo inicial.",
            "estado": "éxito"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "estado": "error"
        }), 500

# Ruta para consultar el saldo de un usuario
@app.route('/saldo/<usuario>', methods=['GET'])
def consultar_saldo(usuario):
    user_ref = db.collection('usuarios').document(usuario)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify(user_doc.to_dict())

# Asegurar que se ejecuta en el puerto correcto en Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Render usa el puerto 10000
    app.run(host='0.0.0.0', port=port)
