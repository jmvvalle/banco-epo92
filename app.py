import json
import os
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar la aplicación Flask
app = Flask(__name__)

# Leer la clave de Firebase desde las variables de entorno en Render
firebase_key = os.getenv("FIREBASE_KEY")

if firebase_key:
    try:
        firebase_key_dict = json.loads(firebase_key.replace("\\n", "\n"))  # Reemplaza \\n por \n
        cred = credentials.Certificate(firebase_key_dict)  # Convertir string JSON a diccionario
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except json.JSONDecodeError:
        raise ValueError("Error al decodificar FIREBASE_KEY. Verifica el formato en Render.")
else:
    raise ValueError("FIREBASE_KEY no está configurada en las variables de entorno.")

# Leer la lista de alumnos desde el archivo JSON
with open("alumnos_corregidos.json", "r", encoding="utf-8") as file:
    alumnos = json.load(file)

# Registrar usuarios en Firestore
def registrar_usuarios_iniciales():
    for alumno in alumnos:
        usuario = alumno["usuario"]
        doc_ref = db.collection("usuarios").document(usuario)

        if not doc_ref.get().exists:  # Evita duplicados
            doc_ref.set({
                "usuario": usuario,
                "nombre": alumno["nombre"],
                "turno": alumno["turno"],
                "grupo": alumno["grupo"],
                "clave": alumno["clave"],  # Contraseña única
                "saldo": 100,  # Saldo inicial
                "transacciones": []  # Lista vacía de transacciones
            })

    return "Usuarios registrados exitosamente."

@app.route('/registrar', methods=['GET'])
def registrar():
    mensaje = registrar_usuarios_iniciales()
    return jsonify({"mensaje": mensaje})

# CONSULTA DE SALDO
@app.route('/consultar', methods=['POST'])
def consultar_saldo():
    data = request.get_json()  # Recibir datos en formato JSON
    usuario = data.get("usuario")
    clave = data.get("clave")

    if not usuario or not clave:
        return jsonify({"error": "Faltan datos"}), 400

    doc_ref = db.collection('usuarios').document(usuario)
    doc = doc_ref.get()

    if doc.exists:
        datos_usuario = doc.to_dict()

        if datos_usuario["clave"] == clave:
            return jsonify({
                "usuario": usuario,
                "nombre": datos_usuario["nombre"],
                "turno": datos_usuario["turno"],
                "grupo": datos_usuario["grupo"],
                "saldo": datos_usuario["saldo"],
                "transacciones": datos_usuario["transacciones"]
            })
        else:
            return jsonify({"error": "Clave incorrecta"}), 401
    else:
        return jsonify({"error": "Usuario no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)
