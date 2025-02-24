import firebase_admin
from firebase_admin import credentials, firestore

# Cargar credenciales desde el archivo JSON que subiste
cred = credentials.Certificate("simulacion-economia.json")  
firebase_admin.initialize_app(cred)

# Conectar con Firestore
db = firestore.client()
