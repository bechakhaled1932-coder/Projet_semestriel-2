from rag.loader import load_pdf
from rag.chunker import split_docs
from rag.embeddings import get_embeddings
from rag.vectorstore import create_index

def test():
    docs = load_pdf("data/test.pdf")
    chunks = split_docs(docs)

    embeddings = get_embeddings()
    db = create_index(chunks, embeddings)

    query = "What is the registration process?"
    results = db.similarity_search(query, k=3)

    for r in results:
        print(r.page_content)

if __name__ == "__main__":
    test()