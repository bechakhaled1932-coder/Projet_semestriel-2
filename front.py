import streamlit as st

def set_page_config():
    st.set_page_config(
        page_title="Assistant ENISo",
        page_icon="🎓",
        layout="centered"
    )

def load_css():
    st.markdown("""
    <style>
        .stApp {
            background-color: #f0f4f8;
        }
        .eniso-header {
            background: linear-gradient(135deg, #1a2f5e 0%, #4a9fd4 100%);
            padding: 30px 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(26, 47, 94, 0.3);
        }
        .eniso-header h1 {
            color: white;
            font-size: 28px;
            font-weight: 700;
            margin: 10px 0 5px 0;
        }
        .eniso-header p {
            color: #cce4f7;
            font-size: 14px;
            margin: 0;
        }
        .eniso-logo-text {
            font-size: 42px;
            font-weight: 900;
            color: white;
            letter-spacing: 3px;
        }
        .eniso-logo-text span {
            color: #4a9fd4;
        }
        .lang-badges {
            display: flex;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 12px;
        }
        .lang-badge {
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 12px;
            border: 1px solid rgba(255,255,255,0.3);
        }
        .stChatMessage {
            border-radius: 12px;
            margin-bottom: 10px;
        }
        .stChatInputContainer {
            border-top: 2px solid #4a9fd4;
            padding-top: 10px;
        }
        .streamlit-expanderHeader {
            background-color: #e8f4fd;
            border-radius: 8px;
            color: #1a2f5e;
        }
        .stats-bar {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            border-left: 4px solid #4a9fd4;
            padding: 10px 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            flex: 1;
        }
        .stat-card .number {
            font-size: 22px;
            font-weight: 700;
            color: #1a2f5e;
        }
        .stat-card .label {
            font-size: 11px;
            color: #888;
        }
        .eniso-footer {
            text-align: center;
            color: #aaa;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
        }
        .stButton button {
            background-color: #1a2f5e;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 5px 15px;
        }
        .stButton button:hover {
            background-color: #4a9fd4;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def show_header():
    st.markdown("""
    <div class="eniso-header">
        <div class="eniso-logo-text">ENI<span>So</span></div>
        <h1>🎓 Assistant Administratif Intelligent</h1>
        <p>École Nationale d'Ingénieurs de Sousse — المدرسة الوطنية للمهندسين بسوسة</p>
        <div class="lang-badges">
            <span class="lang-badge">🇫🇷 Français</span>
            <span class="lang-badge">🇸🇦 العربية</span>
            <span class="lang-badge">🇬🇧 English</span>
            <span class="lang-badge">🇪🇸 Español</span>
            <span class="lang-badge">🇨🇳 中文</span>
            <span class="lang-badge">🇷🇺 Русский</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_stats(nb_docs=4):
    st.markdown(f"""
    <div class="stats-bar">
        <div class="stat-card">
            <div class="number">{nb_docs}</div>
            <div class="label">Documents indexés</div>
        </div>
        <div class="stat-card">
            <div class="number">6+</div>
            <div class="label">Langues supportées</div>
        </div>
        <div class="stat-card">
            <div class="number">24/7</div>
            <div class="label">Disponibilité</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_welcome_message():
    with st.chat_message("assistant"):
        st.markdown("""
👋 **Bonjour et bienvenue à l'ENISo !**

Je suis votre assistant administratif intelligent. Je peux vous aider sur :
- 📋 Les **procédures d'inscription et réinscription**
- 🏢 Les **stages d'été** et leur formulaire
- 🎓 Le **PFE** (Projet de Fin d'Études)
- 📅 Les **emplois du temps**
- 📞 Les **contacts** des services

Posez votre question dans la langue de votre choix ! 🌍
        """)

def show_footer():
    st.markdown("""
    <div class="eniso-footer">
        🏛️ École Nationale d'Ingénieurs de Sousse — ENISo © 2025<br>
        Développé dans le cadre du projet pilote IA
    </div>
    """, unsafe_allow_html=True)

def show_sources(sources):
    if sources:
        with st.expander("📄 Sources utilisées"):
            for i, doc in enumerate(sources):
                st.markdown(f"**Extrait {i+1} :**")
                st.info(doc.page_content)