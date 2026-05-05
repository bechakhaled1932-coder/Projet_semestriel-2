from langchain_community.vectorstores import FAISS

def create_index(docs, embeddings):
    return FAISS.from_documents(docs, embeddings)
