import os
import socket
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
EMBED_MODEL  = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# === Prompt ENISo ===
PROMPT_TEMPLATE = """<s>[INST]
{lang_instruction}

Tu es un assistant administratif de l'ENISo (École Nationale d'Ingénieurs de Sousse).
Tu aides les étudiants concernant les stages, le PFE, les inscriptions et les emplois du temps.

Règles strictes :
1. Réponds UNIQUEMENT dans la langue indiquée ci-dessus
2. Ne traduis JAMAIS ta réponse dans une autre langue
3. N'ajoute JAMAIS de traduction entre parenthèses
4. Réponds uniquement en te basant sur le contexte fourni
5. Si tu ne trouves pas la réponse dans le contexte, dis-le simplement dans la langue demandée

Contexte :
{context}

Question : {question}
[/INST]
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
        input_variables=["context", "question"]
    )

    if is_ollama_available():
        print("✅ Ollama détecté → LLM local Mistral")
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model="mistral", base_url="http://localhost:11434")
    else:
        print("☁️ Ollama non disponible → Groq cloud")
        from langchain_groq import ChatGroq
        try:
            groq_key = st.secrets["GROQ_API_KEY"]
        except:
            groq_key = os.getenv("GROQ_API_KEY")
        llm = ChatGroq(
            api_key=groq_key,
            model_name="llama-3.3-70b-versatile",
            temperature=0
        )

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("✅ Assistant prêt !")
    return chain, retriever


from langdetect import detect

ARABIC_LATIN = [
    "marhaba", "ahlan", "salam", "sabah", "masa", "shukran",
    "afwan", "inshallah", "yalla", "habibi", "kifak", "labas",
    "wach", "bahi", "mlih", "chokran", "barak", "mabrook",
    "tfadhal", "chwiya", "barcha", "tawa", "3andek", "9oulou",
    "mouche", "famma", "haka", "hakka", "aychek", "yesser"
]

def detect_language(text):
    text_lower = text.lower()

    # Arabe en lettres arabes
    if any("\u0600" <= c <= "\u06FF" for c in text):
        return "Arabic", "أجب باللغة العربية الفصحى فقط وبالحروف العربية"

    # Arabe translittéré en latin
    for word in ARABIC_LATIN:
        if word in text_lower:
            return "Arabic", "أجب باللغة العربية الفصحى فقط وبالحروف العربية"

    try:
        lang = detect(text)
        lang_map = {
            "en": ("English", "Respond only in English"),
            "fr": ("French", "Réponds uniquement en français"),
            "ar": ("Arabic", "أجب باللغة العربية الفصحى فقط وبالحروف العربية"),
            "es": ("Spanish", "Responde únicamente en español"),
            "zh-cn": ("Chinese", "只用中文回答"),
            "ru": ("Russian", "Отвечай только на русском языке"),
            "de": ("German", "Antworte nur auf Deutsch"),
            "it": ("Italian", "Rispondi solo in italiano"),
        }
        return lang_map.get(lang, ("English", "Respond only in English"))
    except:
        return "English", "Respond only in English"


def ask(chain, retriever, question):
    lang_name, lang_instruction = detect_language(question)

    question_with_lang = f"""
[LANGUAGE INSTRUCTION - CRITICAL]: {lang_instruction}
[DO NOT USE ANY OTHER LANGUAGE]

Question: {question}
"""

    answer = chain.invoke(question_with_lang)
    sources = retriever.invoke(question)
    return answer, sources