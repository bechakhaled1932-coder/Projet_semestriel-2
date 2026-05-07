import jwt
import bcrypt
from datetime import datetime, timedelta
from pymongo import MongoClient

# Configuration
SECRET_KEY = "eniso-secret-key-2025"
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 24

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["eniso_assistant"]
users_collection = db["users"]
sessions_collection = db["sessions"]

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Sauvegarder la session dans MongoDB
    sessions_collection.insert_one({
        "token": token,
        "user_id": user_id,
        "username": username,
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS),
        "active": True
    })
    return token

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Vérifier que la session est active dans MongoDB
        session = sessions_collection.find_one({
            "token": token,
            "active": True
        })
        if not session:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def register_user(username: str, password: str, email: str) -> dict:
    # Vérifier si l'utilisateur existe déjà
    if users_collection.find_one({"username": username}):
        return {"success": False, "message": "Utilisateur déjà existant"}
    
    hashed = hash_password(password)
    user = {
        "username": username,
        "password": hashed,
        "email": email,
        "created_at": datetime.utcnow(),
        "role": "student"
    }
    result = users_collection.insert_one(user)
    return {"success": True, "user_id": str(result.inserted_id)}

def login_user(username: str, password: str) -> dict:
    user = users_collection.find_one({"username": username})
    if not user:
        return {"success": False, "message": "Utilisateur non trouvé"}
    
    if not verify_password(password, user["password"]):
        return {"success": False, "message": "Mot de passe incorrect"}
    
    token = create_token(str(user["_id"]), username)
    return {"success": True, "token": token, "username": username}

def logout_user(token: str):
    sessions_collection.update_one(
        {"token": token},
        {"$set": {"active": False}}
    )

def save_conversation(token: str, question: str, answer: str, sources: list):
    payload = verify_token(token)
    if not payload:
        return
    
    db["conversations"].insert_one({
        "user_id": payload["user_id"],
        "username": payload["username"],
        "question": question,
        "answer": answer,
        "sources": [s.page_content[:100] for s in sources],
        "timestamp": datetime.utcnow()
    })

def get_user_conversations(token: str) -> list:
    payload = verify_token(token)
    if not payload:
        return []
    
    convos = list(db["conversations"].find(
        {"user_id": payload["user_id"]},
        {"_id": 0, "question": 1, "answer": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(20))
    return convos