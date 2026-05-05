from langchain_community.vectorstores import FAISS

def build_vectorstore(chunks, embeddings):
    return FAISS.from_documents(chunks, embeddings)

def save_vectorstore(vs, path="faiss_index"):
    vs.save_local(path)

def load_vectorstore(embeddings, path="faiss_index"):
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
