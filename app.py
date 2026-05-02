import os
import glob
import streamlit as st
from ingest import load_documents, split_documents, create_vectordb
from rag_pipeline import load_rag_chain, ask
from front import (
    set_page_config, load_css, show_header,
    show_stats, show_welcome_message,
    show_footer, show_sources
)

# === Config ===
set_page_config()
load_css()
show_header()

# === Chargement RAG ===
@st.cache_resource
def setup():
    vectordb_dir = "vectordb"
    chroma_files = glob.glob(f"{vectordb_dir}/**/*", recursive=True)
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

# === Stats ===
show_stats(nb_docs=4)

# === Historique ===
if "messages" not in st.session_state:
    st.session_state.messages = []

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
        st.rerun()

# === Chat ===
if question := st.chat_input("Posez votre question... / اطرح سؤالك... / Ask your question..."):

    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("⏳ Recherche en cours..."):
            answer, sources = ask(chain, retriever, question)
        st.markdown(answer)
        show_sources(sources)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# === Footer ===
show_footer()