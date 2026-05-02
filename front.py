import streamlit as st

def set_page_config():
    st.set_page_config(
        page_title="Assistant ENISo",
        page_icon="🎓",
        layout="wide"
    )

def load_css():
    st.markdown("""
    <style>
        /* Fond général */
        .stApp { background-color: #f0f4f8; }

        /* Cacher menu streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Header */
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

        /* Stats */
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

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: white;
            border-right: 0.5px solid #ccc;
        }
        [data-testid="stSidebar"] .stMarkdown p {
            color: #333;
            font-size: 14px;
        }

        /* Messages chat */
        [data-testid="stChatMessage"] {
            background: white;
            border: 0.5px solid #ddd;
            border-radius: 12px;
            color: #111;
        }

        /* Input chat */
        [data-testid="stChatInput"] {
            border-top: 2px solid #4a9fd4;
        }

        /* Boutons */
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

        /* Expander sources */
        .streamlit-expanderHeader {
            background: #e8f4fd;
            color: #1a2f5e;
            font-weight: 500;
        }
        .streamlit-expanderContent {
            background: #f7fbff;
            color: #111;
        }

        /* Footer */
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
    st.markdown("""
    <div class="eniso-header">
        <div class="eniso-header-top">
            <div class="eniso-logo-circle">
                 <img src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgIHhtbG5zOmNjPSJodHRwOi8vY3JlYXRpdmVjb21tb25zLm9yZy9ucyMiCiAgIHhtbG5zOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIgogICB3aWR0aD0iNTI5LjI1IgogICBoZWlnaHQ9IjU2My41OTM3NSIKICAgaWQ9InN2ZzIiCiAgIHZlcnNpb249IjEuMSI+" 
                 width="52" height="52" style="object-fit:contain; border-radius:50%;"/>
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
👋 **Bonjour et bienvenue à l'ENISo !**

Je suis votre assistant administratif intelligent. Je peux vous aider sur :
- 📋 Les **procédures d'inscription et réinscription**
- 🏢 Les **stages d'été** et leur formulaire
- 🎓 Le **PFE** (Projet de Fin d'Études)
- 📅 Les **emplois du temps**
- 📞 Les **contacts** des services

Posez votre question dans la langue de votre choix ! 🌍
        """)

def show_sources(sources):
    if sources:
        with st.expander("📄 Sources utilisées"):
            for i, doc in enumerate(sources):
                st.markdown(f"**Extrait {i+1} :**")
                st.info(doc.page_content)

def show_footer():
    st.markdown("""
    <div class="eniso-footer">
        🏛️ École Nationale d'Ingénieurs de Sousse — ENISo © 2025<br>
        Développé dans le cadre du projet pilote IA
    </div>
    """, unsafe_allow_html=True)