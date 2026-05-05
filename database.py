from pymongo import MongoClient
from datetime import datetime

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client["eniso_assistant"]
    collection = db["conversations"]
    print("✅ MongoDB connecté")
except Exception as e:
    print(f"⚠️ MongoDB non disponible : {e}")
    collection = None

def save_conversation(question, answer, sources, feedback=None):
    if collection is None:
        return
    doc = {
        "timestamp": datetime.now(),
        "question": question,
        "answer": answer,
        "sources": [s.page_content[:100] for s in sources],
        "feedback": feedback
    }
    collection.insert_one(doc)

def get_stats():
    if collection is None:
        return {"total": 0, "utiles": 0, "taux_satisfaction": "0%"}
    total = collection.count_documents({})
    utiles = collection.count_documents({"feedback": "👍"})
    return {
        "total": total,
        "utiles": utiles,
        "taux_satisfaction": f"{(utiles/total*100):.1f}%" if total > 0 else "0%"
    }

def export_for_finetuning():
    if collection is None:
        return []
    good = list(collection.find(
        {"feedback": "👍"},
        {"_id": 0, "question": 1, "answer": 1}
    ))
    import json
    dataset = [{"instruction": c["question"], "output": c["answer"]} for c in good]
    with open("dataset_from_real_data.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    print(f"✅ {len(dataset)} exemples exportés")
    return dataset