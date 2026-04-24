import streamlit as st
from rag_pipeline import load_rag_chain, ask

# === Configuration de la page ===
st.set_page_config(
    page_title="Assistant ENISo",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Assistant Administratif ENISo")
st.caption("Posez vos questions sur les procédures administratives, stages, PFE et emplois du temps.")

# === Chargement du RAG (une seule fois) ===
@st.cache_resource
def get_chain():
    chain, retriever = load_rag_chain()
    return chain, retriever

chain, retriever = get_chain()

# === Historique de conversation ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# Afficher l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# === Zone de saisie ===
if question := st.chat_input("Posez votre question..."):

    # Afficher la question
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # Générer la réponse
    with st.chat_message("assistant"):
        with st.spinner("⏳ Recherche en cours..."):
            answer, sources = ask(chain, retriever, question)
        st.markdown(answer)

        # Afficher les sources
        if sources:
            with st.expander("📄 Sources utilisées"):
                for i, doc in enumerate(sources):
                    st.markdown(f"**Extrait {i+1} :**")
                    st.info(doc.page_content)

    st.session_state.messages.append({"role": "assistant", "content": answer})