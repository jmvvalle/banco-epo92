from flask import Flask, request, jsonify
from firebase_config import db
import json

app = Flask(__name__)

# Cargar alumnos desde el archivo JSON
with open("alumnos_corregidos.json", "r", encoding="utf-8") as file:
    alumnos = json.load(file)

@app.route('/cargar_alumnos', methods=['POST'])
def cargar_alumnos():
    try:
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

@app.route('/saldo/<usuario>', methods=['GET'])
def consultar_saldo(usuario):
    user_ref = db.collection('usuarios').document(usuario)
    user_doc = user_ref.get()

    if not user_doc.exists:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify(user_doc.to_dict())

if __name__ == '__main__':
    app.run(debug=True)
