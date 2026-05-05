import os
import glob
import streamlit as st
from ingest import load_documents, split_documents, create_vectordb
from rag_pipeline import load_rag_chain, ask, get_llm_mode
from front import (
    set_page_config, load_css, show_header,
    show_stats, show_welcome_message, get_real_stats,
    show_footer, show_sources
)

# === Import MongoDB (optionnel) ===
try:
    from database import save_conversation, get_stats
    MONGODB_AVAILABLE = True
except:
    MONGODB_AVAILABLE = False

# === Dictionnaire des messages de feedback multilingue ===
FEEDBACK_MESSAGES = {
    "fr": ("👍 Merci !", "👎 Merci pour votre retour !"),
    "en": ("👍 Thanks!", "👎 Thanks for your feedback!"),
    "ar": ("👍 شكراً!", "👎 شكراً على تقييمك!"),
    "es": ("👍 ¡Gracias!", "👎 ¡Gracias por tu comentario!"),
    "de": ("👍 Danke!", "👎 Danke für dein Feedback!"),
    "it": ("👍 Grazie!", "👎 Grazie per il feedback!"),
    "zh": ("👍 谢谢！", "👎 感谢您的反馈！"),
    "ru": ("👍 Спасибо!", "👎 Спасибо за отзыв!"),
    "default": ("👍 Merci !", "👎 Merci pour votre retour !")
}

def get_feedback_message(lang_name, feedback_type):
    """Retourne le message de feedback dans la bonne langue"""
    lang_key = lang_name.lower()
    if lang_key == "arabic":
        lang_key = "ar"
    elif lang_key == "english":
        lang_key = "en"
    elif lang_key == "french":
        lang_key = "fr"
    elif lang_key == "spanish":
        lang_key = "es"
    elif lang_key == "german":
        lang_key = "de"
    elif lang_key == "italian":
        lang_key = "it"
    elif lang_key == "chinese":
        lang_key = "zh"
    elif lang_key == "russian":
        lang_key = "ru"
    else:
        lang_key = "default"
    
    msgs = FEEDBACK_MESSAGES.get(lang_key, FEEDBACK_MESSAGES["default"])
    return msgs[0] if feedback_type == "like" else msgs[1]

# === Config ===
set_page_config()
load_css()

# === Récupérer le mode LLM ===
llm_mode = get_llm_mode()
show_header(mode=llm_mode)

# === Chargement RAG ===
@st.cache_resource
def setup():
    vectordb_dir = "vectordb"
    chroma_files = glob.glob(f"{vectordb_dir}/**/*.parquet", recursive=True)
    if not chroma_files:
        st.info("⏳ Initialisation de la base de connaissances...")
        docs = load_documents()
        st.write(f"📄 {len(docs)} documents chargés")
        chunks = split_documents(docs)
        st.write(f"✂️ {len(chunks)} chunks créés")
        create_vectordb(chunks)
        st.success("✅ Base vectorielle créée !")
    chain, retriever = load_rag_chain()
    return chain, retriever

chain, retriever = setup()

# === Stats dynamiques ===
real_nb_docs, real_nb_langues = get_real_stats()
show_stats(nb_docs=real_nb_docs, nb_langues=real_nb_langues)

# === Historique ===
if "messages" not in st.session_state:
    st.session_state.messages = []

if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = {}

if "last_language" not in st.session_state:
    st.session_state.last_language = "fr"

if not st.session_state.messages:
    show_welcome_message()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === Reset ===
col1, col2 = st.columns([5, 1])
with col2:
    if st.button("🗑️ Reset"):
        st.session_state.messages = []
        st.session_state.feedback_given = {}
        st.rerun()

# === Chat ===
if question := st.chat_input("Posez votre question... / اطرح سؤالك... / Ask your question..."):

    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("⏳ Recherche en cours..."):
            answer, sources, lang_name = ask(chain, retriever, question)
        st.markdown(answer)
        show_sources(sources)
        st.session_state.last_language = lang_name

        # === Feedback avec messages multilingues ===
        msg_id = len(st.session_state.messages)
        if msg_id not in st.session_state.feedback_given:
            st.write("**Cette réponse vous a-t-elle aidé ?**")
            col_like, col_dislike, col_empty = st.columns([1, 1, 4])
            with col_like:
                if st.button("👍", key=f"like_{msg_id}"):
                    if MONGODB_AVAILABLE:
                        save_conversation(question, answer, sources, "👍")
                    st.session_state.feedback_given[msg_id] = "👍"
                    st.success(get_feedback_message(lang_name, "like"))
            with col_dislike:
                if st.button("👎", key=f"dislike_{msg_id}"):
                    if MONGODB_AVAILABLE:
                        save_conversation(question, answer, sources, "👎")
                    st.session_state.feedback_given[msg_id] = "👎"
                    st.info(get_feedback_message(lang_name, "dislike"))
        else:
            fb = st.session_state.feedback_given[msg_id]
            fb_text = "👍" if fb == "👍" else "👎"
            st.write(f"Feedback enregistré : {fb_text}")

    st.session_state.messages.append({"role": "assistant", "content": answer})

# === Stats MongoDB dans sidebar ===
if MONGODB_AVAILABLE:
    try:
        with st.sidebar:
            st.markdown("---")
            st.markdown("**📊 Statistiques**")
            stats = get_stats()
            st.metric("Total conversations", stats["total"])
            st.metric("Réponses utiles", stats["utiles"])
            st.metric("Satisfaction", stats["taux_satisfaction"])
    except:
        pass

# === Footer ===
show_footer()