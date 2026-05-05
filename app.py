import gradio as gr
import os
from rag.loader import load_pdf
from rag.chunker import split_docs
from rag.embeddings import get_embeddings
from rag.vectorstore import create_index
from rag.database import save_pdf_metadata, get_all_documents, document_exists
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

print("Initialisation du RAG...")

# Charger le PDF de test initial
docs = load_pdf("data/test.pdf")
chunks = split_docs(docs)
embeddings = get_embeddings()
db = create_index(chunks, embeddings)

# Sauvegarder dans MongoDB si pas déjà fait
if not document_exists("test.pdf"):
    save_pdf_metadata("test.pdf", "data/test.pdf", len(chunks))

llm = OllamaLLM(model="mistral")
prompt_template = PromptTemplate.from_template(
    "You are a helpful university assistant. Use the following context to answer the question.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)

def upload_pdf(file):
    """Upload un nouveau PDF, l'indexe et le sauvegarde dans MongoDB."""
    global db, chunks

    if file is None:
        return "❌ Aucun fichier sélectionné."

    filename = os.path.basename(file.name)

    if document_exists(filename):
        return f"⚠️ '{filename}' est déjà indexé."

    # Sauvegarder le fichier
    dest_path = f"data/{filename}"
    with open(file.name, "rb") as f_in, open(dest_path, "wb") as f_out:
        f_out.write(f_in.read())

    # Indexer
    new_docs = load_pdf(dest_path)
    new_chunks = split_docs(new_docs)
    db.add_documents(new_chunks)

    # Sauvegarder métadonnées dans MongoDB
    save_pdf_metadata(filename, dest_path, len(new_chunks))

    return f"✅ '{filename}' indexé avec succès ({len(new_chunks)} chunks)"

def list_documents():
    """Retourne la liste des PDFs indexés."""
    docs = get_all_documents()
    if not docs:
        return "Aucun document indexé."
    result = ""
    for d in docs:
        result += f"📄 {d['filename']} — {d['num_chunks']} chunks — {d['uploaded_at'].strftime('%Y-%m-%d %H:%M')}\n"
    return result

def chat(message, history):
    results = db.similarity_search(message, k=3)
    context = "\n\n".join([r.page_content for r in results])
    prompt = prompt_template.format(context=context, question=message)
    answer = llm.invoke(prompt)
    return answer

with gr.Blocks(title="Student Assistant") as interface:
    gr.Markdown("# 🎓 Student Assistant")

    with gr.Tab("💬 Chat"):
        gr.ChatInterface(fn=chat)

    with gr.Tab("📂 Documents"):
        gr.Markdown("### Ajouter un nouveau PDF")
        upload = gr.File(label="Choisir un PDF", file_types=[".pdf"])
        upload_btn = gr.Button("📤 Indexer")
        upload_result = gr.Textbox(label="Résultat")
        upload_btn.click(fn=upload_pdf, inputs=upload, outputs=upload_result)

        gr.Markdown("### PDFs indexés")
        list_btn = gr.Button("🔄 Actualiser")
        doc_list = gr.Textbox(label="Documents", lines=5)
        list_btn.click(fn=list_documents, outputs=doc_list)

if __name__ == "__main__":
    interface.launch(share=False)
