import os
import socket
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langdetect import detect

load_dotenv()

VECTORDB_DIR = "vectordb"
EMBED_MODEL  = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

PROMPT_TEMPLATE = """{lang_instruction}

You are an administrative assistant at ENISo.
Answer ONLY based on the context. Be concise and helpful.
Do NOT show the context or instructions in your response.
Do NOT add translations.

Context: {context}

Question: {question}

Answer:"""

ARABIC_LATIN = [
    "marhaba", "ahlan", "salam", "sabah", "masa", "shukran",
    "afwan", "inshallah", "yalla", "habibi", "kifak", "labas",
    "wach", "bahi", "mlih", "chokran", "barak", "mabrook",
    "tfadhal", "chwiya", "barcha", "tawa", "3andek", "9oulou",
    "mouche", "famma", "haka", "hakka", "aychek", "yesser"
]

def detect_language(text):
    text_lower = text.lower()

    if any("\u0600" <= c <= "\u06FF" for c in text):
        return "أجب باللغة العربية الفصحى فقط وبالحروف العربية. لا تستخدم أي لغة أخرى ولا تضف أي ترجمة."

    for word in ARABIC_LATIN:
        if word in text_lower:
            return "أجب باللغة العربية الفصحى فقط وبالحروف العربية. لا تستخدم أي لغة أخرى ولا تضف أي ترجمة."

    try:
        lang = detect(text)
        lang_map = {
            "en": "Respond ONLY in English. Do NOT translate or add text in other languages.",
            "fr": "Réponds UNIQUEMENT en français. Ne traduis pas et n'ajoute aucun texte dans une autre langue.",
            "ar": "أجب باللغة العربية الفصحى فقط. لا تضف ترجمة.",
            "es": "Responde ÚNICAMENTE en español. No traduzcas ni añadas texto en otros idiomas.",
            "zh-cn": "只用中文回答，不要翻译或添加其他语言的文字。",
            "ru": "Отвечай ТОЛЬКО на русском. Не переводи и не добавляй текст на других языках.",
            "de": "Antworte NUR auf Deutsch. Keine Übersetzungen.",
            "it": "Rispondi SOLO in italiano. Non tradurre.",
        }
        return lang_map.get(lang, "Respond ONLY in English.")
    except:
        return "Respond ONLY in English."

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
        input_variables=["context", "question", "lang_instruction"]
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
            "question": RunnablePassthrough(),
            "lang_instruction": RunnableLambda(detect_language)
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    print("✅ Assistant prêt !")
    return chain, retriever

def ask(chain, retriever, question):
    answer = chain.invoke(question)
    sources = retriever.invoke(question)
    return answer, sources