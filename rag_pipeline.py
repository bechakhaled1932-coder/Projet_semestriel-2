import os
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

# === Configuration ===
VECTORDB_DIR = "vectordb"
EMBED_MODEL  = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def get_groq_key():
    # Essayer d'abord les secrets Streamlit, puis .env
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.getenv("GROQ_API_KEY")

# === Prompt ENISo ===
PROMPT_TEMPLATE = """
Tu es un assistant administratif de l'ENISo (École Nationale d'Ingénieurs de Sousse).
Tu aides les étudiants à trouver des informations sur les procédures administratives,
les stages, le PFE, les inscriptions et les emplois du temps.

Réponds uniquement en te basant sur le contexte fourni.
Si tu ne trouves pas la réponse dans le contexte, dis-le clairement.
Détecte automatiquement la langue de la question posée par l'étudiant et réponds
dans cette même langue. Si la question est en arabe, réponds en arabe.
Si la question est en français, réponds en français.
Si la question est en anglais, réponds en anglais.

Contexte :
{context}

Question : {question}

Réponse :
"""
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

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

    print("⏳ Chargement du LLM Groq...")
    llm = ChatGroq(
        api_key=get_groq_key(),
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )

    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
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