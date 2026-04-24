from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# === Configuration ===
VECTORDB_DIR = "vectordb"
EMBED_MODEL  = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
LLM_MODEL    = "mistral"

# === Prompt personnalisé ENISo ===
PROMPT_TEMPLATE = """
Tu es un assistant administratif de l'ENISo (École Nationale d'Ingénieurs de Sousse).
Tu aides les étudiants à trouver des informations sur les procédures administratives,
les stages, le PFE, les inscriptions et les emplois du temps.

Réponds uniquement en te basant sur le contexte fourni.
Si tu ne trouves pas la réponse dans le contexte, dis-le clairement.
Réponds toujours en français.

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

    print("⏳ Chargement du LLM Mistral...")
    llm = OllamaLLM(model=LLM_MODEL)

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