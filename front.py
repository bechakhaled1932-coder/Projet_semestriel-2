import base64
import pathlib
import streamlit as st

def get_logo_base64():
    logo_path = pathlib.Path("assets/logo.svg")
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

def set_page_config():
    st.set_page_config(
        page_title="Assistant ENISo",
        page_icon="🎓",
        layout="wide"
    )

def load_css():
    st.markdown("""
    <style>
        # Ajoutez ceci dans le bloc <style> de load_css()
    [data-testid="stChatMessageContent"] p {
        color: #111111 !important;
    }
    [data-testid="stChatMessageContent"] {
        color: #111111 !important;
    }
        .stApp { background-color: #f0f4f8; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .eniso-header {
            background: #1a2f5e;
            padding: 20px 24px 16px;
            border-radius: 12px;
            margin-bottom: 14px;
        }
        .eniso-header-top {
            display: flex;
            align-items: center;
            gap: 14px;
            margin-bottom: 12px;
        }
        .eniso-logo-circle {
            width: 60px;
            height: 60px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            padding: 4px;
        }
        .eniso-header-titles h1 {
            color: #ffffff;
            font-size: 20px;
            font-weight: 600;
            margin: 0;
        }
        .eniso-header-titles p {
            color: #a8d4f0;
            font-size: 12px;
            margin: 4px 0 0 0;
        }
        .eniso-lang-row {
            display: flex;
            gap: 6px;
            flex-wrap: wrap;
        }
        .eniso-lang-pill {
            background: rgba(255,255,255,0.15);
            color: #ffffff;
            font-size: 11px;
            padding: 3px 9px;
            border-radius: 20px;
            border: 0.5px solid rgba(255,255,255,0.35);
        }
        .eniso-stats-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 14px;
        }
        .eniso-stat {
            background: white;
            border-radius: 8px;
            padding: 10px 14px;
            border-left: 3px solid #4a9fd4;
            border-top: 0.5px solid #ccc;
            border-right: 0.5px solid #ccc;
            border-bottom: 0.5px solid #ccc;
        }
        .eniso-stat-num {
            font-size: 22px;
            font-weight: 600;
            color: #1a2f5e;
        }
        .eniso-stat-lbl {
            font-size: 11px;
            color: #555;
            margin-top: 2px;
        }
        [data-testid="stSidebar"] {
            background: white;
            border-right: 0.5px solid #ccc;
        }
        [data-testid="stSidebar"] .stMarkdown p {
            color: #333;
            font-size: 14px;
        }
        [data-testid="stChatMessage"] {
    background: white;
    border: 0.5px solid #ddd;
    border-radius: 12px;
    color: #111111 !important;
}
[data-testid="stChatMessageContent"] {
    color: #111111 !important;
}
[data-testid="stChatMessageContent"] p {
    color: #111111 !important;
}
[data-testid="stChatMessageContent"] li {
    color: #111111 !important;
}
[data-testid="stChatMessageContent"] strong {
    color: #111111 !important;
}
        .stButton button {
            background-color: #1a2f5e;
            color: white;
            border-radius: 8px;
            border: none;
        }
        .stButton button:hover {
            background-color: #4a9fd4;
            color: white;
        }
        .streamlit-expanderHeader {
            background: #e8f4fd;
            color: #1a2f5e;
            font-weight: 500;
        }
        .streamlit-expanderContent {
            background: #f7fbff;
            color: #111;
        }
        .eniso-footer {
            text-align: center;
            color: #555;
            font-size: 11px;
            margin-top: 20px;
            padding-top: 12px;
            border-top: 0.5px solid #ccc;
        }
    </style>
    """, unsafe_allow_html=True)

def show_header():
    logo_b64 = get_logo_base64()
    if logo_b64:
        logo_html = f'<img src="data:image/svg+xml;base64,{logo_b64}" width="52" height="52" style="object-fit:contain;"/>'
    else:
        logo_html = '<span style="font-size:12px;font-weight:700;color:#1a2f5e;">ENISo</span>'

    st.markdown(f"""
    <div class="eniso-header">
        <div class="eniso-header-top">
            <div class="eniso-logo-circle">
                {logo_html}
            </div>
            <div class="eniso-header-titles">
                <h1>🎓 Assistant Administratif Intelligent</h1>
                <p>École Nationale d'Ingénieurs de Sousse — المدرسة الوطنية للمهندسين بسوسة</p>
            </div>
        </div>
        <div class="eniso-lang-row">
            <span class="eniso-lang-pill">🇫🇷 Français</span>
            <span class="eniso-lang-pill">🇸🇦 العربية</span>
            <span class="eniso-lang-pill">🇬🇧 English</span>
            <span class="eniso-lang-pill">🇪🇸 Español</span>
            <span class="eniso-lang-pill">🇨🇳 中文</span>
            <span class="eniso-lang-pill">🇷🇺 Русский</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_stats(nb_docs=4):
    st.markdown(f"""
    <div class="eniso-stats-row">
        <div class="eniso-stat">
            <div class="eniso-stat-num">{nb_docs}</div>
            <div class="eniso-stat-lbl">Documents indexés</div>
        </div>
        <div class="eniso-stat">
            <div class="eniso-stat-num">6+</div>
            <div class="eniso-stat-lbl">Langues supportées</div>
        </div>
        <div class="eniso-stat">
            <div class="eniso-stat-num">24/7</div>
            <div class="eniso-stat-lbl">Disponibilité</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_sidebar():
    with st.sidebar:
        st.markdown("### 🏛️ ENISo")
        st.markdown("---")
        st.markdown("**Navigation**")
        st.markdown("💬 Chat")
        st.markdown("📋 Inscription")
        st.markdown("🏢 Stages")
        st.markdown("🎓 PFE")
        st.markdown("📅 Emploi du temps")
        st.markdown("📞 Contacts")
        st.markdown("---")
        st.markdown("**À propos**")
        st.markdown("Assistant IA basé sur RAG")
        st.markdown("Modèle : LLaMA 3.3 70B")
        st.markdown("Base : ChromaDB")
def show_welcome_message():
    with st.chat_message("assistant"):
        st.markdown("""
<div style="color: #111111; font-size: 14px;">

👋 <strong>Bonjour et bienvenue à l'ENISo !</strong>

Je suis votre assistant administratif intelligent. Je peux vous aider sur :
<ul>
<li>📋 Les <strong>procédures d'inscription et réinscription</strong></li>
<li>🏢 Les <strong>stages d'été</strong> et leur formulaire</li>
<li>🎓 Le <strong>PFE</strong> (Projet de Fin d'Études)</li>
<li>📅 Les <strong>emplois du temps</strong></li>
<li>📞 Les <strong>contacts</strong> des services</li>
</ul>

Posez votre question dans la langue de votre choix ! 🌍

</div>
""", unsafe_allow_html=True)

def show_sources(sources):
    if sources:
        with st.expander("📄 Sources utilisées"):
            for i, doc in enumerate(sources):
                st.markdown(f"**Extrait {i+1} :**")
                st.info(doc.page_content)

def show_footer():
    st.markdown("""
    <div class="eniso-footer">
        🏛️ École Nationale d'Ingénieurs de Sousse — ENISo © 2026<br>
        Développé dans le cadre du projet pilote IA
    </div>
    """, unsafe_allow_html=True)