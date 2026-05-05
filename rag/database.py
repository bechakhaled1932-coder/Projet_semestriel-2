from pymongo import MongoClient
from datetime import datetime

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["student_assistant"]
collection = db["documents"]
history_collection = db["history"]
feedback_collection = db["feedback"]

def save_pdf_metadata(filename: str, filepath: str, num_chunks: int) -> str:
    doc = {
        "filename": filename,
        "filepath": filepath,
        "num_chunks": num_chunks,
        "uploaded_at": datetime.now(),
        "indexed": True
    }
    result = collection.insert_one(doc)
    print(f"✅ MongoDB: PDF '{filename}' sauvegardé")
    return str(result.inserted_id)

def get_all_documents():
    return list(collection.find({}, {"_id": 0, "filename": 1, "uploaded_at": 1, "num_chunks": 1}))

def document_exists(filename: str) -> bool:
    return collection.find_one({"filename": filename}) is not None

def save_question(question: str, answer: str, sources: list) -> None:
    history_collection.insert_one({
        "question": question,
        "answer": answer,
        "sources": sources,
        "asked_at": datetime.now()
    })

def get_history(limit: int = 20) -> list:
    return list(history_collection.find(
        {}, {"_id": 0, "question": 1, "answer": 1, "sources": 1, "asked_at": 1}
    ).sort("asked_at", -1).limit(limit))

def save_feedback(question: str, answer: str, rating: str) -> None:
    feedback_collection.insert_one({
        "question": question,
        "answer": answer,
        "rating": rating,
        "created_at": datetime.now()
    })

def get_feedback_stats() -> dict:
    total = feedback_collection.count_documents({})
    positive = feedback_collection.count_documents({"rating": "👍"})
    negative = feedback_collection.count_documents({"rating": "👎"})
    return {"total": total, "positive": positive, "negative": negative}

def get_stats() -> dict:
    total_docs = collection.count_documents({})
    total_questions = history_collection.count_documents({})
    feedback_stats = get_feedback_stats()

    pipeline = [
        {"$group": {"_id": "$question", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_questions = list(history_collection.aggregate(pipeline))

    pipeline2 = [
        {"$unwind": "$sources"},
        {"$group": {"_id": "$sources", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_sources = list(history_collection.aggregate(pipeline2))

    return {
        "total_docs": total_docs,
        "total_questions": total_questions,
        "feedback": feedback_stats,
        "top_questions": top_questions,
        "top_sources": top_sources
    }

def delete_document(filename: str) -> bool:
    """Supprime un document de MongoDB."""
    result = collection.delete_one({"filename": filename})
    return result.deleted_count > 0
