from pymongo import MongoClient
from datetime import datetime
import os

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["student_assistant"]
collection = db["documents"]

def save_pdf_metadata(filename: str, filepath: str, num_chunks: int) -> str:
    """Sauvegarde les métadonnées d'un PDF dans MongoDB."""
    doc = {
        "filename": filename,
        "filepath": filepath,
        "num_chunks": num_chunks,
        "uploaded_at": datetime.now(),
        "indexed": True
    }
    result = collection.insert_one(doc)
    print(f"✅ MongoDB: PDF '{filename}' sauvegardé (id: {result.inserted_id})")
    return str(result.inserted_id)

def get_all_documents():
    """Retourne la liste de tous les PDFs indexés."""
    return list(collection.find({}, {"_id": 0, "filename": 1, "uploaded_at": 1, "num_chunks": 1}))

def document_exists(filename: str) -> bool:
    """Vérifie si un PDF est déjà indexé."""
    return collection.find_one({"filename": filename}) is not None
