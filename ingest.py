import os
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# === Configuration ===
DOCUMENTS_DIR = "documents"
VECTORDB_DIR  = "vectordb"
EMBED_MODEL   = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def load_documents():
    docs = []
    for filename in os.listdir(DOCUMENTS_DIR):
        filepath = os.path.join(DOCUMENTS_DIR, filename)
        if filename.endswith(".pdf"):
            print(f"📄 Chargement PDF : {filename}")
            loader = PyPDFLoader(filepath)
            docs.extend(loader.load())
        elif filename.endswith(".docx"):
            print(f"📄 Chargement Word : {filename}")
            loader = Docx2txtLoader(filepath)
            docs.extend(loader.load())
        elif filename.endswith(".txt"):
            print(f"📄 Chargement TXT : {filename}")
            loader = TextLoader(filepath, encoding="utf-8")
            docs.extend(loader.load())
    print(f"✅ {len(docs)} pages chargées au total")
    return docs

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ {len(chunks)} chunks créés")
    return chunks

def create_vectordb(chunks):
    print("⏳ Génération des embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORDB_DIR
    )
    print(f"✅ Base vectorielle créée dans '{VECTORDB_DIR}'")
    return db

if __name__ == "__main__":
    print("=== Ingestion des documents ENISo ===")
    docs   = load_documents()
    chunks = split_documents(docs)
    db     = create_vectordb(chunks)
    print("\n🎉 Ingestion terminée ! Vous pouvez lancer app.py")