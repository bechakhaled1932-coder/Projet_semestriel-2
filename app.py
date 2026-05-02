import os
import glob
import streamlit as st
from ingest import load_documents, split_documents, create_vectordb
from rag_pipeline import load_rag_chain, ask

# === Configuration de la page ===
st.set_page_config(
    page_title="Assistant ENISo",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Assistant Administratif ENISo")
st.caption("Posez vos questions sur les procédures administratives, stages, PFE et emplois du temps.")

# === Ingestion automatique si vectordb vide ===
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

# === Historique de conversation ===
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === Zone de saisie ===
if question := st.chat_input("Posez votre question..."):

    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("⏳ Recherche en cours..."):
            answer, sources = ask(chain, retriever, question)
        st.markdown(answer)

        if sources:
            with st.expander("📄 Sources utilisées"):
                for i, doc in enumerate(sources):
                    st.markdown(f"**Extrait {i+1} :**")
                    st.info(doc.page_content)

    st.session_state.messages.append({"role": "assistant", "content": answer})