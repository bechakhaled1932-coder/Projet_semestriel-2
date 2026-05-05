import os
import socket
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langdetect import detect

load_dotenv()

# === Configuration ===
VECTORDB_DIR = "vectordb"
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Liste des mots Darija en caractères latins
ARABIC_LATIN_WORDS = [
    "marhaba", "ahlan", "salam", "sabah", "masa", "shukran",
    "afwan", "inshallah", "yalla", "habibi", "kifak", "labas",
    "wach", "bahi", "mlih", "chokran", "barak", "mabrook",
    "tfadhal", "chwiya", "barcha", "tawa", "3andek", "9oulou",
    "mouche", "famma", "haka", "hakka", "aychek", "yesser"
]

# === Prompt ENISo avec système de langue renforcé ===
PROMPT_TEMPLATE = """You are the ENISo administrative assistant.

LANGUAGE RULE - STRICT ENFORCEMENT:
{lang_instruction}

You MUST follow this rule. Do not use any other language.
Answer using ONLY the context below. If the answer is not in the context, say so in the required language.

CONTEXT:
{context}

QUESTION: {question}

ANSWER (in the required language only):"""

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def is_ollama_available():
    try:
        s = socket.create_connection(("localhost", 11434), timeout=1)
        s.close()
        return True
    except:
        return False

def detect_language(text):
    """Détecte la langue et retourne (nom, instruction_llm)"""
    text_lower = text.lower()

    # Arabe unicode
    if any("\u0600" <= c <= "\u06FF" for c in text):
        return "Arabe", "Respond only in Arabic. Use Arabic script. أجب بالعربية فقط."

    # Darija latin
    for word in ARABIC_LATIN_WORDS:
        if word in text_lower:
            return "Arabe", "Respond only in Arabic. Use Arabic script. أجب بالعربية فقط."

    try:
        lang = detect(text)
        lang_map = {
            "fr": ("Français", "Respond only in French. Réponds uniquement en français."),
            "en": ("English", "Respond only in English."),
            "ar": ("Arabe", "Respond only in Arabic. أجب بالعربية فقط."),
            "es": ("Español", "Respond only in Spanish. Responde únicamente en español."),
            "zh-cn": ("中文", "Respond only in Chinese. 只用中文回答。"),
            "ru": ("Русский", "Respond only in Russian. Отвечай только на русском."),
            "de": ("Deutsch", "Respond only in German. Antworte nur auf Deutsch."),
            "it": ("Italiano", "Respond only in Italian. Rispondi solo in italiano."),
        }
        return lang_map.get(lang, ("English", "Respond only in English."))
    except:
        return "English", "Respond only in English."

def get_llm_mode():
    if is_ollama_available():
        return "🟢 Local (Ollama/Mistral)"
    else:
        return "☁️ Cloud (Groq/Llama 3.3)"

def load_rag_chain():
    print("⏳ Chargement de la base vectorielle...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma(persist_directory=VECTORDB_DIR, embedding_function=embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question", "lang_instruction"]
    )

    if is_ollama_available():
        print("✅ Ollama → Mistral local")
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model="mistral", base_url="http://localhost:11434", temperature=0)
    else:
        print("☁️ Groq → Llama 3.3")
        from langchain_groq import ChatGroq
        try:
            groq_key = st.secrets["GROQ_API_KEY"]
        except:
            groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("❌ GROQ_API_KEY non trouvée")
        llm = ChatGroq(api_key=groq_key, model_name="llama-3.3-70b-versatile", temperature=0)

    def retrieve_and_format(inputs):
        docs = retriever.invoke(inputs["question"])
        return {
            "context": format_docs(docs),
            "question": inputs["question"],
            "lang_instruction": inputs["lang_instruction"]
        }

    chain = RunnableLambda(retrieve_and_format) | prompt | llm | StrOutputParser()
    print("✅ Assistant prêt !")
    return chain, retriever

def ask(chain, retriever, question):
    lang_name, lang_instruction = detect_language(question)
    print(f"🔍 Langue détectée : {lang_name}")
    
    answer = chain.invoke({
        "question": question,
        "lang_instruction": lang_instruction
    })
    sources = retriever.invoke(question)
    return answer, sources, lang_name