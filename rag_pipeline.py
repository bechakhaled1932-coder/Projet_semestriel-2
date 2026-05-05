import os
import socket
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
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

# === Prompt ENISo ===
PROMPT_TEMPLATE = """
You are an administrative assistant at ENISo (École Nationale d'Ingénieurs de Sousse).
You help students find information about administrative procedures, internships, PFE, registrations and schedules.

CRITICAL RULE - LANGUAGE DETECTION:
- The user's question is in the language specified below
- You MUST respond ONLY in that exact same language
- NEVER mix languages in your response
- NEVER respond in a different language than the question

Answer ONLY based on the provided context.
If you cannot find the answer in the context, say so clearly IN THE SAME LANGUAGE.

Context:
{context}

Question: {question}

Language instruction: {lang_instruction}

Answer (in the EXACT same language as requested):
"""

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
    """Détecte la langue du texte et retourne (nom_langue, instruction_prompt)"""
    text_lower = text.lower()

    # Arabe en lettres arabes
    if any("\u0600" <= c <= "\u06FF" for c in text):
        return "Arabic", "أجب باللغة العربية الفصحى فقط"

    # Arabe translittéré en latin (Darija)
    for word in ARABIC_LATIN_WORDS:
        if word in text_lower:
            return "Arabic", "أجب باللغة العربية الفصحى فقط"

    try:
        lang = detect(text)
        lang_map = {
            "en": ("English", "Respond only in English"),
            "fr": ("French", "Réponds uniquement en français"),
            "ar": ("Arabic", "أجب باللغة العربية الفصحى فقط"),
            "es": ("Spanish", "Responde únicamente en español"),
            "zh-cn": ("Chinese", "只用中文回答"),
            "ru": ("Russian", "Отвечай только на русском языке"),
            "de": ("German", "Antworte nur auf Deutsch"),
            "it": ("Italian", "Rispondi solo in italiano"),
        }
        return lang_map.get(lang, ("English", "Respond only in English"))
    except:
        return "English", "Respond only in English"

def get_llm_mode():
    """Retourne le mode actuel pour affichage"""
    if is_ollama_available():
        return "🟢 Local (Ollama/Mistral)"
    else:
        return "☁️ Cloud (Groq/Llama 3.3)"

def load_rag_chain():
    print("⏳ Chargement de la base vectorielle...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma(
        persist_directory=VECTORDB_DIR,
        embedding_function=embeddings
    )
    retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question", "lang_instruction"]
    )

    if is_ollama_available():
        print("✅ Ollama détecté → LLM local Mistral")
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model="mistral", base_url="http://localhost:11434", temperature=0)
    else:
        print("☁️ Ollama non disponible → Groq cloud")
        from langchain_groq import ChatGroq
        try:
            groq_key = st.secrets["GROQ_API_KEY"]
        except:
            groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError("❌ GROQ_API_KEY non trouvée dans st.secrets ou .env")
        llm = ChatGroq(
            api_key=groq_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0
        )

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "lang_instruction": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("✅ Assistant prêt !")
    return chain, retriever

def ask(chain, retriever, question):
    lang_name, lang_instruction = detect_language(question)
    # On passe la question et l'instruction séparément
    answer = chain.invoke({"question": question, "lang_instruction": lang_instruction})
    sources = retriever.invoke(question)
    return answer, sources, lang_name