import gradio as gr
from auth import login_user, register_user, logout_user, verify_token, save_conversation, get_user_conversations
from rag_pipeline import load_rag_chain, ask

# Charger le RAG
chain, retriever = load_rag_chain()

# === Interface Login ===
def login(username, password):
    result = login_user(username, password)
    if result["success"]:
        return (
            result["token"],
            f"✅ Connecté en tant que {result['username']}",
            gr.update(visible=False),  # cacher login
            gr.update(visible=True)    # afficher chat
        )
    return "", f"❌ {result['message']}", gr.update(visible=True), gr.update(visible=False)

def register(username, password, email):
    result = register_user(username, password, email)
    if result["success"]:
        return "✅ Compte créé ! Connectez-vous maintenant."
    return f"❌ {result['message']}"

def chat(message, history, token):
    if not token:
        return history + [["", "❌ Veuillez vous connecter d'abord."]], ""
    
    payload = verify_token(token)
    if not payload:
        return history + [["", "❌ Session expirée. Reconnectez-vous."]], ""
    
    answer, sources = ask(chain, retriever, message)
    
    # Sauvegarder dans MongoDB
    save_conversation(token, message, answer, sources)
    
    history.append([message, answer])
    return history, ""

def load_history(token):
    if not token:
        return []
    convos = get_user_conversations(token)
    history = [[c["question"], c["answer"]] for c in convos]
    return history

def logout(token):
    logout_user(token)
    return (
        "",
        "✅ Déconnecté",
        gr.update(visible=True),   # afficher login
        gr.update(visible=False)   # cacher chat
    )

# === Interface Gradio ===
with gr.Blocks(
    title="Assistant ENISo",
    theme=gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="slate"
    ),
    css="""
    .header { text-align: center; padding: 20px; background: #1a2f5e; border-radius: 10px; margin-bottom: 20px; }
    .header h1 { color: white; }
    .header p { color: #a8d4f0; }
    """
) as demo:

    # Token stocké dans l'état
    token_state = gr.State("")

    # === Header ===
    gr.HTML("""
    <div class="header">
        <h1>🎓 Assistant Administratif ENISo</h1>
        <p>École Nationale d'Ingénieurs de Sousse — المدرسة الوطنية للمهندسين بسوسة</p>
    </div>
    """)

    # === Section Login ===
    with gr.Column(visible=True) as login_section:
        gr.Markdown("## 🔐 Connexion")
        with gr.Tab("Se connecter"):
            username_input = gr.Textbox(label="Nom d'utilisateur")
            password_input = gr.Textbox(label="Mot de passe", type="password")
            login_btn = gr.Button("Se connecter", variant="primary")
            login_msg = gr.Textbox(label="Message", interactive=False)

        with gr.Tab("Créer un compte"):
            reg_username = gr.Textbox(label="Nom d'utilisateur")
            reg_password = gr.Textbox(label="Mot de passe", type="password")
            reg_email = gr.Textbox(label="Email")
            reg_btn = gr.Button("Créer le compte", variant="secondary")
            reg_msg = gr.Textbox(label="Message", interactive=False)

    # === Section Chat ===
    with gr.Column(visible=False) as chat_section:
        gr.Markdown("## 💬 Chat")
        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(height=500, label="Assistant ENISo")
                with gr.Row():
                    msg_input = gr.Textbox(
                        placeholder="Posez votre question... / اطرح سؤالك... / Ask your question...",
                        scale=4
                    )
                    send_btn = gr.Button("Envoyer", variant="primary", scale=1)
            
            with gr.Column(scale=1):
                gr.Markdown("### 📋 Historique")
                history_btn = gr.Button("Charger mon historique")
                logout_btn = gr.Button("🚪 Déconnexion", variant="stop")

    # === Events ===
    login_btn.click(
        login,
        inputs=[username_input, password_input],
        outputs=[token_state, login_msg, login_section, chat_section]
    )

    reg_btn.click(
        register,
        inputs=[reg_username, reg_password, reg_email],
        outputs=[reg_msg]
    )

    send_btn.click(
        chat,
        inputs=[msg_input, chatbot, token_state],
        outputs=[chatbot, msg_input]
    )

    msg_input.submit(
        chat,
        inputs=[msg_input, chatbot, token_state],
        outputs=[chatbot, msg_input]
    )

    history_btn.click(
        load_history,
        inputs=[token_state],
        outputs=[chatbot]
    )

    logout_btn.click(
        logout,
        inputs=[token_state],
        outputs=[token_state, login_msg, login_section, chat_section]
    )

# Lancer l'app
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )