import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

# Cargar credenciales desde la variable de entorno
firebase_key = os.getenv("FIREBASE_KEY")

if not firebase_key:
    raise ValueError("No se encontró la variable de entorno FIREBASE_KEY")

cred_dict = json.loads(firebase_key)
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

# Conectar con Firestore
db = firestore.client()
