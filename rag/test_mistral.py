from rag.loader import load_pdf
from rag.chunker import split_docs
from rag.embeddings import get_embeddings
from rag.vectorstore import create_index
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

def test_mistral():
    print("Chargement du PDF...")
    docs = load_pdf("data/test.pdf")
    chunks = split_docs(docs)
    embeddings = get_embeddings()
    db = create_index(chunks, embeddings)

    llm = OllamaLLM(model="mistral")

    prompt_template = PromptTemplate.from_template(
        "Use the following context to answer the question.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    questions = [
        "What is the registration process?",
        "What documents are needed for internships?",
        "When is the PFE submission deadline?"
    ]

    for question in questions:
        print(f"\nQ: {question}")
        results = db.similarity_search(question, k=3)
        context = "\n\n".join([r.page_content for r in results])
        prompt = prompt_template.format(context=context, question=question)
        answer = llm.invoke(prompt)
        print(f"A: {answer}")

if __name__ == "__main__":
    test_mistral()
