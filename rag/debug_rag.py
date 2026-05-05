from rag.loader import load_pdf
from rag.chunker import split_docs
from rag.embeddings import get_embeddings
from rag.vectorstore import create_index

docs = load_pdf("data/test.pdf")
print(f"Pages chargées : {len(docs)}")

chunks = split_docs(docs)
print(f"Chunks créés : {len(chunks)}")
print(f"\n--- Chunk 1 ---\n{chunks[0].page_content}")
print(f"\n--- Chunk 2 ---\n{chunks[1].page_content}")

embeddings = get_embeddings()
db = create_index(chunks, embeddings)
print(f"\nVectorstore créé avec {db.index.ntotal} vecteurs")

query = "registration documents"
results = db.similarity_search(query, k=2)
print(f"\n--- Résultats similarité pour '{query}' ---")
for i, r in enumerate(results):
    print(f"\nRésultat {i+1} (score pertinent):\n{r.page_content}")
