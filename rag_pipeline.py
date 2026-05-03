import os
import socket
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# === Configuration ===
VECTORDB_DIR = "vectordb"
EMBED_MODEL  = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# === Prompt ENISo ===
PROMPT_TEMPLATE = """
You are an administrative assistant at ENISo (École Nationale d'Ingénieurs de Sousse).
You help students find information about administrative procedures, internships, PFE, registrations and schedules.

CRITICAL RULE - LANGUAGE DETECTION:
- Detect the language of the user's question
- You MUST respond ONLY in that exact same language
- If the question is in English → respond in English
- If the question is in French → respond in French
- Si la question est en français → réponds en français
- إذا كان السؤال بالعربية → أجب بالعربية
- Si la pregunta es en español → responde en español
- 如果问题是中文 → 用中文回答
- Если вопрос на русском → отвечай на русском
- NEVER mix languages in your response
- NEVER respond in a different language than the question

Answer ONLY based on the provided context.
If you cannot find the answer in the context, say so clearly IN THE SAME LANGUAGE as the question.

Context:
{context}

Question: {question}

Answer (in the EXACT same language as the question):
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


def ask(chain, retriever, question):
    answer = chain.invoke(question)
    sources = retriever.invoke(question)
    return answer, sources