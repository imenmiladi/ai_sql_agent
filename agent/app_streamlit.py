import streamlit as st
import os
import pandas as pd
import sqlite3
from langchain_community.callbacks import StreamlitCallbackHandler
from orchestrator import create_agent, DB_PATH

# =========================
# 1. Configuration & CSS "Pro"
# =========================
st.set_page_config(page_title="AI Data Analyst", page_icon="📈", layout="wide")

st.markdown("""
<style>
    /* Import de police Google (Optionnel, sinon utilise défaut) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Couleur de fond plus douce */
    .stApp {
        background-color: #f0f2f6;
    }

    /* Style des cartes (Containers blancs avec ombre) */
    .css-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* Titres */
    h1 { color: #1e3a8a; }
    h2, h3 { color: #3b82f6; }

    /* Bouton personnalisé */
    div.stButton > button:first-child {
        background-color: #2563eb;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    div.stButton > button:first-child:hover {
        background-color: #1d4ed8;
    }
    
    /* Zone de logs de l'agent */
    .stExpander {
        background-color: white;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# 2. Fonctions Utilitaires
# =========================
@st.cache_resource
def load_agent():
    return create_agent()

def get_db_schema():
    """Récupère la liste des tables pour aider l'utilisateur"""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

# =========================
# 3. Sidebar : Panneau de Contrôle
# =========================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3090/3090108.png", width=80)
    st.title("Settings")
    
    st.markdown("### 🗄️ Base de données")
    if os.path.exists(DB_PATH):
        st.success("Connectée")
        # Petit explorateur de schema
        with st.expander("Voir les tables disponibles"):
            tables = get_db_schema()
            if tables:
                for t in tables:
                    st.code(t, language="text")
            else:
                st.write("Aucune table trouvée.")
    else:
        st.error("Non trouvée")
        st.stop()

    st.markdown("---")
    st.markdown("### ℹ️ Aide")
    st.info("Cet agent peut générer du SQL, analyser les données et tracer des graphiques. Soyez précis dans vos demandes.")

# =========================
# 4. Interface Principale
# =========================

# Header Section
col_logo, col_title = st.columns([1, 10])
with col_logo:
    st.write("") # Spacer
with col_title:
    st.markdown("<h1>📊 AI Data Analyst <span style='font-size:0.5em; color:gray'>v2.0</span></h1>", unsafe_allow_html=True)

# Gestion de l'état (Session State) pour garder les résultats affichés
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Bonjour ! Je suis prêt à analyser vos données. Quelle est votre question ?"}]
if "last_viz" not in st.session_state:
    st.session_state["last_viz"] = None

# Input Utilisateur (Style Chat)
user_input = st.chat_input("Ex: Quel est le chiffre d'affaires par catégorie ? (Graphique barre)")

# Affichage de l'historique (Optionnel, ici on garde simple : juste la dernière interaction complexe)
# Pour une vraie app de chat, on bouclerait sur st.session_state["messages"]
# Ici, on focus sur le mode "Rapport"

if user_input:
    # 1. Afficher la question utilisateur
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Préparation de la réponse
    with st.chat_message("assistant"):
        st_callback_container = st.container()
        st_callback = StreamlitCallbackHandler(st_callback_container, expand_new_thoughts=True)
        
        agent_executor = load_agent()
        
        # Zone de "Pensée" avec un Spinner propre
        with st.status("🔍 Analyse en cours...", expanded=True) as status:
            try:
                response = agent_executor.invoke(
                    {"input": user_input},
                    config={"callbacks": [st_callback]}
                )
                status.update(label="✅ Analyse terminée !", state="complete", expanded=False)
                
                # Récupération de la réponse texte
                output_text = response.get("output", "")
                
                # Récupération intelligente de l'image
                viz_path = response.get("visualization_path")
                # Fallback : chercher le fichier le plus récent si l'agent a oublié le path
                if not viz_path:
                    viz_dir = "visualizations"
                    if os.path.exists(viz_dir):
                        files = [os.path.join(viz_dir, f) for f in os.listdir(viz_dir) if f.endswith('.png')]
                        if files:
                            viz_path = max(files, key=os.path.getctime)
                
                # Stockage en session
                st.session_state["last_result"] = output_text
                st.session_state["last_viz"] = viz_path
                
            except Exception as e:
                status.update(label="❌ Erreur", state="error")
                st.error(f"Erreur : {e}")

# =========================
# 5. Affichage des Résultats (Card Layout)
# =========================
if "last_result" in st.session_state:
    st.markdown("---")
    
    # Utilisation de Tabs pour organiser l'information proprement
    tab1, tab2, tab3 = st.tabs(["📝 Insights & Réponse", "📊 Visualisation", "💾 Données Brutes"])
    
    with tab1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Analyse de l'IA")
        st.write(st.session_state["last_result"])
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        viz = st.session_state.get("last_viz")
        if viz and os.path.exists(viz):
            col_img, col_dl = st.columns([4, 1])
            with col_img:
                st.image(viz, caption="Graphique généré", use_column_width=True)
            with col_dl:
                with open(viz, "rb") as file:
                    st.download_button(
                        label="📥 Télécharger",
                        data=file,
                        file_name=os.path.basename(viz),
                        mime="image/png"
                    )
        else:
            st.info("Aucune visualisation générée pour cette demande.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with tab3:
        # Bonus : Essayer de trouver le dernier CSV exporté pour l'afficher
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("### Fichiers sources")
        export_dir = "exports"
        if os.path.exists(export_dir):
            csv_files = [os.path.join(export_dir, f) for f in os.listdir(export_dir) if f.endswith('.csv')]
            if csv_files:
                latest_csv = max(csv_files, key=os.path.getctime)
                st.write(f"Dernier fichier de données utilisé : `{os.path.basename(latest_csv)}`")
                df = pd.read_csv(latest_csv)
                st.dataframe(df, use_container_width=True)
            else:
                st.write("Pas de fichier CSV trouvé.")
        st.markdown('</div>', unsafe_allow_html=True)