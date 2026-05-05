import gradio as gr
import os
import plotly.graph_objects as go
from langdetect import detect
from rag.loader import load_pdf
from rag.chunker import split_docs
from rag.embeddings import get_embeddings
from rag.vectorstore import create_index
from rag.database import (save_pdf_metadata, get_all_documents, document_exists,
                           save_question, get_history, save_feedback, get_feedback_stats,
                           get_stats, delete_document)
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

print("Initialisation du RAG...")
embeddings = get_embeddings()

# Charger TOUS les PDFs indexés dans MongoDB
all_docs_meta = get_all_documents()
all_chunks = []

for doc_meta in all_docs_meta:
    filepath = doc_meta.get("filepath") or f"data/{doc_meta['filename']}"
    if os.path.exists(filepath):
        try:
            docs = load_pdf(filepath)
            chunks = split_docs(docs)
            all_chunks.extend(chunks)
            print(f"✅ Chargé : {doc_meta['filename']}")
        except Exception as e:
            print(f"⚠️ Erreur {doc_meta['filename']} : {e}")

# Si aucun PDF trouvé, charger test.pdf par défaut
if not all_chunks:
    print("⚠️ Aucun PDF trouvé, chargement de test.pdf...")
    docs = load_pdf("data/test.pdf")
    all_chunks = split_docs(docs)
    if not document_exists("test.pdf"):
        save_pdf_metadata("test.pdf", "data/test.pdf", len(all_chunks))

db = create_index(all_chunks, embeddings)
print(f"✅ FAISS prêt avec {len(all_chunks)} chunks au total")

llm = OllamaLLM(model="mistral")

prompt_fr = PromptTemplate.from_template(
    "Tu es un assistant universitaire. Utilise le contexte pour répondre en français.\n\nContexte:\n{context}\n\nQuestion: {question}\n\nRéponse:"
)
prompt_en = PromptTemplate.from_template(
    "You are a helpful university assistant. Use the context to answer in English.\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
)
prompt_ar = PromptTemplate.from_template(
    "أنت مساعد جامعي. استخدم السياق للإجابة باللغة العربية.\n\nالسياق:\n{context}\n\nالسؤال: {question}\n\nالإجابة:"
)

last_interaction = {"question": "", "answer": ""}

def get_prompt(question: str):
    try:
        lang = detect(question)
    except:
        lang = "fr"
    if lang == "ar":
        return prompt_ar
    elif lang == "en":
        return prompt_en
    else:
        return prompt_fr

def upload_pdf(file):
    global db
    if file is None:
        return "❌ Aucun fichier sélectionné."
    filename = os.path.basename(file.name)
    if document_exists(filename):
        return f"⚠️ '{filename}' est déjà indexé."
    dest_path = f"data/{filename}"
    with open(file.name, "rb") as f_in, open(dest_path, "wb") as f_out:
        f_out.write(f_in.read())
    new_docs = load_pdf(dest_path)
    new_chunks = split_docs(new_docs)
    db.add_documents(new_chunks)
    save_pdf_metadata(filename, dest_path, len(new_chunks))
    return f"✅ '{filename}' indexé avec succès ({len(new_chunks)} chunks)"

def list_documents():
    docs = get_all_documents()
    if not docs:
        return "Aucun document indexé."
    result = ""
    for d in docs:
        result += f"📄 {d['filename']} — {d['num_chunks']} chunks — {d['uploaded_at'].strftime('%Y-%m-%d %H:%M')}\n"
    return result

def delete_pdf(filename: str):
    filename = filename.strip()
    if not filename:
        return "❌ Entrez un nom de fichier."
    if not document_exists(filename):
        return f"⚠️ '{filename}' introuvable dans la base."
    delete_document(filename)
    filepath = f"data/{filename}"
    if os.path.exists(filepath):
        os.remove(filepath)
    return f"✅ '{filename}' supprimé avec succès."

def chat(message, history):
    global last_interaction
    results = db.similarity_search(message, k=3)
    context = "\n\n".join([r.page_content for r in results])
    prompt_template = get_prompt(message)
    prompt = prompt_template.format(context=context, question=message)
    answer = llm.invoke(prompt)

    sources = []
    for r in results:
        source = r.metadata.get("source", "inconnu")
        page = r.metadata.get("page", "?")
        filename = os.path.basename(source)
        src = f"📄 {filename} — page {page}"
        if src not in sources:
            sources.append(src)

    save_question(message, answer, sources)
    last_interaction = {"question": message, "answer": answer}
    sources_text = "\n".join(sources)
    return f"{answer}\n\n---\n🔎 Sources :\n{sources_text}"

def show_history():
    history = get_history(limit=20)
    if not history:
        return "Aucune question posée pour l'instant."
    result = ""
    for h in history:
        date = h['asked_at'].strftime('%Y-%m-%d %H:%M')
        result += f"🕐 {date}\n❓ {h['question']}\n💬 {h['answer'][:150]}...\n🔎 {', '.join(h['sources'])}\n{'─'*50}\n"
    return result

def give_feedback(rating: str):
    if not last_interaction["question"]:
        return "⚠️ Posez d'abord une question."
    save_feedback(last_interaction["question"], last_interaction["answer"], rating)
    stats = get_feedback_stats()
    return f"✅ Feedback '{rating}' enregistré !\n👍 {stats['positive']}  👎 {stats['negative']}  Total: {stats['total']}"

def chart_feedback():
    """Camembert 👍 vs 👎"""
    stats = get_feedback_stats()
    if stats['total'] == 0:
        fig = go.Figure()
        fig.add_annotation(text="Aucun feedback encore", x=0.5, y=0.5, showarrow=False, font_size=18)
        fig.update_layout(title="Feedback des étudiants")
        return fig
    fig = go.Figure(data=[go.Pie(
        labels=["👍 Positif", "👎 Négatif"],
        values=[stats['positive'], stats['negative']],
        hole=0.4,
        marker_colors=["#2ecc71", "#e74c3c"]
    )])
    fig.update_layout(
        title="Feedback des étudiants",
        font=dict(size=14)
    )
    return fig

def chart_top_documents():
    """Bar chart des documents les plus consultés"""
    stats = get_stats()
    if not stats['top_sources']:
        fig = go.Figure()
        fig.add_annotation(text="Aucune donnée encore", x=0.5, y=0.5, showarrow=False, font_size=18)
        fig.update_layout(title="Documents les plus consultés")
        return fig
    docs = [s['_id'].replace("📄 ", "")[:30] for s in stats['top_sources']]
    counts = [s['count'] for s in stats['top_sources']]
    fig = go.Figure(data=[go.Bar(
        x=counts,
        y=docs,
        orientation='h',
        marker_color="#3498db"
    )])
    fig.update_layout(
        title="Documents les plus consultés",
        xaxis_title="Nombre de consultations",
        font=dict(size=13)
    )
    return fig

def chart_questions_per_day():
    """Courbe des questions par heure aujourd'hui"""
    from collections import defaultdict
    history = get_history(limit=100)
    if not history:
        fig = go.Figure()
        fig.add_annotation(text="Aucune question encore", x=0.5, y=0.5, showarrow=False, font_size=18)
        fig.update_layout(title="Questions par heure")
        return fig
    counts = defaultdict(int)
    for h in history:
        try:
            hour = h['asked_at'].strftime('%Y-%m-%d %H:00')
        except:
            hour = "inconnu"
        counts[hour] += 1
    hours = sorted([h for h in counts.keys() if h != "inconnu"])
    values = [counts[h] for h in hours]
    fig = go.Figure(data=[go.Bar(
        x=hours,
        y=values,
        marker_color="#9b59b6"
    )])
    fig.update_layout(
        title="Questions posées par heure",
        xaxis_title="Heure",
        yaxis_title="Nombre de questions",
        font=dict(size=13)
    )
    return fig

def refresh_all_charts():
    return chart_feedback(), chart_top_documents(), chart_questions_per_day()

with gr.Blocks(title="Student Assistant") as interface:
    gr.Markdown("# 🎓 Student Assistant")

    with gr.Tab("💬 Chat"):
        gr.ChatInterface(fn=chat)
        gr.Markdown("### Cette réponse était utile ?")
        with gr.Row():
            btn_up = gr.Button("👍 Oui")
            btn_down = gr.Button("👎 Non")
        feedback_result = gr.Textbox(label="", lines=2)
        btn_up.click(fn=lambda: give_feedback("👍"), outputs=feedback_result)
        btn_down.click(fn=lambda: give_feedback("👎"), outputs=feedback_result)

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

        gr.Markdown("### Supprimer un PDF")
        delete_input = gr.Textbox(label="Nom du fichier (ex: test.pdf)")
        delete_btn = gr.Button("🗑️ Supprimer")
        delete_result = gr.Textbox(label="Résultat")
        delete_btn.click(fn=delete_pdf, inputs=delete_input, outputs=delete_result)

    with gr.Tab("📜 Historique"):
        gr.Markdown("### Dernières questions posées")
        history_btn = gr.Button("🔄 Actualiser")
        history_box = gr.Textbox(label="Historique", lines=20)
        history_btn.click(fn=show_history, outputs=history_box)

    with gr.Tab("📊 Statistiques"):
        gr.Markdown("### Tableau de bord analytique")
        refresh_btn = gr.Button("🔄 Actualiser les graphiques")
        with gr.Row():
            plot_feedback = gr.Plot(label="Feedback")
            plot_docs = gr.Plot(label="Documents consultés")
        plot_questions = gr.Plot(label="Questions par jour")
        refresh_btn.click(
            fn=refresh_all_charts,
            outputs=[plot_feedback, plot_docs, plot_questions]
        )

if __name__ == "__main__":
    interface.launch(share=False)
