import streamlit as st
import os
import json
import re
from pathlib import Path
from datetime import datetime
import pandas as pd
from PIL import Image

# Import de votre agent (assurez-vous que le fichier principal s'appelle agent.py)
try:
    from orchestrator import create_agent
    DB_PATH = "data/boutique.db"
    EXPORT_DIR = "exports"
    VIZ_DIR = "visualizations"
except ImportError:
    st.error("⚠️ Impossible d'importer l'agent. Vérifiez que tous les fichiers sont présents.")
    st.stop()

# Configuration de la page
st.set_page_config(
    page_title="Agent Data Analyst AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stChatMessage p {
        color: #000000 !important;
    }
    .tool-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.85em;
        font-weight: 600;
        margin: 5px 5px 5px 0;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    .result-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
    .download-section {
        display: flex;
        gap: 10px;
        margin-top: 15px;
        flex-wrap: wrap;
    }
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .stDownloadButton>button {
        background-color: #667eea;
        color: white !important;
        border-radius: 8px;
    }
    .stDownloadButton>button:hover {
        background-color: #5568d3;
    }
    .stDownloadButton>button p, .stDownloadButton>button span, .stDownloadButton>button div {
        color: white !important;
    }
    .sql-code {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        color: #000000;
        margin: 10px 0;
    }
    /* Forcer le texte en noir dans les LISTES du chat */
    .stChatMessage ul li,
    .stChatMessage ol li {
        color: #000000 !important;
    }
    .sql-code {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        color: #000000;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de la session
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent' not in st.session_state:
    if os.path.exists(DB_PATH):
        st.session_state.agent = create_agent()
    else:
        st.error(f"⚠️ Base de données introuvable : {DB_PATH}")
        st.stop()

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/chatbot.png", width=80)
    st.title("🤖 Agent AI")
    st.markdown("---")
    
    st.markdown("### 📊 Capacités")
    st.markdown("""
    - 🔍 Analyse de données SQL
    - 📈 Génération de graphiques
    - 📥 Export CSV
    - 💬 Conversation naturelle
    """)
    
    st.markdown("---")
    
    if st.button("🗑️ Effacer l'historique", use_container_width=True):
        st.session_state.messages = []
        # Supprimer les fichiers dans visualizations
        for file in Path(VIZ_DIR).glob("*.png"):
            try:
                file.unlink()
            except:
                pass
        # Supprimer les fichiers dans exports
        for file in Path(EXPORT_DIR).glob("*.csv"):
            try:
                file.unlink()
            except:
                pass
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📝 Exemples de questions")
    exemples = [
        "Pourcentage de chaque marque dans le stock",
        "Top 5 produits les plus chers",
        "Répartition des tailles disponibles",
        "Liste des produits Zara en taille M"
    ]
    
    for exemple in exemples:
        if st.button(f"💡 {exemple}", key=f"exemple_{exemple}", use_container_width=True):
            st.session_state.user_input = exemple

# Header principal
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🤖 Assistant Data Analyst IA")
    st.markdown("*Posez vos questions en langage naturel - L'IA s'occupe du reste*")

with col2:
    st.metric("📊 Statut", "En ligne", delta="Actif")

st.markdown("---")

# Zone de chat
chat_container = st.container()

with chat_container:
    # Affichage des messages précédents
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
            
            # Affichage des outils utilisés
            if "tools" in message and message["tools"]:
                tools_html = "🔧 **Outils utilisés :** "
                for tool in message["tools"]:
                    if "SQL" in tool:
                        tools_html += '<span class="tool-badge">⚡ Génération SQL</span> '
                    elif "Exécuteur" in tool:
                        tools_html += '<span class="tool-badge">🗄️ Exécution requête</span> '
                    elif "visualisation" in tool:
                        tools_html += '<span class="tool-badge">📊 Création graphique</span> '
                st.markdown(tools_html, unsafe_allow_html=True)
            
            # Affichage des résultats
            if "results" in message:
                results = message["results"]
                msg_id = message.get("msg_id", "default")
                
                # Affichage de la requête SQL
                if "sql_query" in results and results["sql_query"]:
                    st.markdown("---")
                    st.markdown("**📝 Requête SQL générée :**")
                    st.code(results["sql_query"], language="sql")
                
                # Affichage de l'aperçu CSV
                if "csv_path" in results and results["csv_path"] and os.path.exists(results["csv_path"]):
                    st.markdown("---")
                    st.markdown("**📊 Aperçu des données :**")
                    df = pd.read_csv(results["csv_path"])
                    st.dataframe(df, use_container_width=True)
                
                # Affichage du graphique
                if "viz_path" in results and results["viz_path"] and os.path.exists(results["viz_path"]):
                    st.markdown("---")
                    st.markdown("**📈 Visualisation :**")
                    st.image(results["viz_path"], use_container_width=True)
                
                # Section téléchargement
                if results.get("csv_path") or results.get("viz_path") or results.get("sql_query"):
                    st.markdown("---")
                    st.markdown("**📥 Téléchargements :**")
                    st.markdown('<div class="download-section">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if "csv_path" in results and results["csv_path"] and os.path.exists(results["csv_path"]):
                            with open(results["csv_path"], "rb") as f:
                                st.download_button(
                                    label="📥 Télécharger CSV",
                                    data=f,
                                    file_name=os.path.basename(results["csv_path"]),
                                    mime="text/csv",
                                    use_container_width=True,
                                    key=f"hist_csv_{msg_id}"
                                )
                    
                    with col2:
                        if "viz_path" in results and results["viz_path"] and os.path.exists(results["viz_path"]):
                            with open(results["viz_path"], "rb") as f:
                                st.download_button(
                                    label="🖼️ Télécharger Image",
                                    data=f,
                                    file_name=os.path.basename(results["viz_path"]),
                                    mime="image/png",
                                    use_container_width=True,
                                    key=f"hist_img_{msg_id}"
                                )
                    
                    with col3:
                        if "sql_query" in results and results["sql_query"]:
                            st.download_button(
                                label="💾 Télécharger SQL",
                                data=results["sql_query"],
                                file_name=f"query_{msg_id}.sql",
                                mime="text/plain",
                                use_container_width=True,
                                key=f"hist_sql_{msg_id}"
                            )
                    
                    st.markdown('</div>', unsafe_allow_html=True)

# Input utilisateur
user_query = st.chat_input("💬 Posez votre question ici...")

# Vérifier si une question a été cliquée depuis la sidebar
if "user_input" in st.session_state:
    user_query = st.session_state.user_input
    del st.session_state.user_input

if user_query:
    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Réponse de l'assistant
    with st.chat_message("assistant"):
        # Placeholder pour les outils
        tools_placeholder = st.empty()
        response_placeholder = st.empty()
        
        tools_used = []
        
        try:
            # Capture de la sortie verbose pour détecter les outils
            import io
            import sys
            from contextlib import redirect_stdout
            
            # Affichage initial
            tools_placeholder.markdown("**Analyse de la requête...**")
            
            f = io.StringIO()
            with redirect_stdout(f):
                result = st.session_state.agent.invoke({"input": user_query})
            
            output = f.getvalue()
            
            # Détection des outils utilisés
            if "generate_sql_query" in output or "generate_visualization" in output or "execute_and_export_sql" in output:
                # Affichage progressif des outils au fur et à mesure
                tools_html = "**🔧 Raisonnement :** "
                
                if "generate_sql_query" in output:
                    tools_used.append("Générateur SQL")
                    tools_html += '<span class="tool-badge">⚡ Génération SQL</span> '
                    tools_placeholder.markdown(tools_html, unsafe_allow_html=True)
                
                if "execute_and_export_sql" in output:
                    tools_used.append("Exécuteur SQL")
                    tools_html += '<span class="tool-badge">🗄️ Exécution requête</span> '
                    tools_placeholder.markdown(tools_html, unsafe_allow_html=True)
                
                if "generate_visualization" in output:
                    tools_used.append("Générateur de visualisation")
                    tools_html += '<span class="tool-badge">📊 Création graphique</span>'
                    tools_placeholder.markdown(tools_html, unsafe_allow_html=True)
            else:
                # Pas d'outils utilisés, on efface le message de raisonnement
                tools_placeholder.empty()
            
            # Extraction des fichiers générés (uniquement les plus récents de cette session)
            csv_path = None
            viz_path = None
            sql_query = None
            
            # Sauvegarder le timestamp actuel pour ne récupérer que les nouveaux fichiers
            current_time = datetime.now()
            
            # Recherche du dernier CSV généré (dans les 10 dernières secondes)
            csv_files = sorted(Path(EXPORT_DIR).glob("*.csv"), key=os.path.getmtime, reverse=True)
            if csv_files:
                csv_mtime = os.path.getmtime(csv_files[0])
                if (current_time.timestamp() - csv_mtime) < 10:  # Fichier créé il y a moins de 10 secondes
                    csv_path = str(csv_files[0])
            
            # Recherche du dernier graphique généré (dans les 10 dernières secondes)
            viz_files = sorted(Path(VIZ_DIR).glob("*.png"), key=os.path.getmtime, reverse=True)
            if viz_files:
                viz_mtime = os.path.getmtime(viz_files[0])
                if (current_time.timestamp() - viz_mtime) < 10:  # Fichier créé il y a moins de 10 secondes
                    viz_path = str(viz_files[0])
            
            # Extraction de la requête SQL du output
            sql_match = re.search(
            r'"sql"\s*:\s*"(.*?)"\s*(,|\})',
            output,
            re.DOTALL
            )       

            if sql_match:
                sql_query = sql_match.group(1).replace('\\"', '"').strip()
            # Affichage de la réponse
            response_text = result.get('output', '')
            
            # Nettoyage de la réponse pour extraire uniquement le texte pertinent
            if response_text:
                # Vérifier si c'est déjà une liste
                if isinstance(response_text, list):
                    # Extraire le texte du premier élément
                    if len(response_text) > 0 and isinstance(response_text[0], dict):
                        response_text = response_text[0].get('text', '')
                    else:
                        response_text = str(response_text)
                
                # Convertir en string si ce n'est pas déjà le cas
                response_text = str(response_text)
                
                # Si la réponse contient la structure [{'type': 'text', ...}]
                if "[{'type': 'text'" in response_text or '[{"type": "text"' in response_text:
                    # Extraction du texte entre les guillemets
                    import ast
                    try:
                        # Parse la structure
                        parsed = ast.literal_eval(response_text)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            response_text = parsed[0].get('text', response_text)
                    except:
                        # Si le parsing échoue, essayer avec regex
                        match = re.search(r"'text':\s*'([^']*(?:\\'[^']*)*)'", response_text)
                        if match:
                            response_text = match.group(1).replace("\\'", "'")
                
                # Nettoyer les chemins de fichiers du texte
                if isinstance(response_text, str):
                    lines = response_text.split('\n')
                    clean_lines = []
                    for line in lines:
                        # Ignorer les lignes qui contiennent des chemins, métadonnées ou listes à puces
                        if not any(x in line.lower() for x in [
                            'visualizations\\', 'exports\\', 'disponible ici', 
                            '.png', '.csv', 'graphique a été généré', 
                            'fichier:', 'chemin:', 'path:', 'signature'
                        ]):
                            # Ignorer les lignes qui commencent par * (listes à puces)
                            if line.strip() and not line.strip().startswith('*'):
                                clean_lines.append(line)
                    
                    response_text = '\n'.join(clean_lines).strip()
            
            # Si après nettoyage il ne reste rien, on met un message par défaut
            if not response_text:
                response_text = "Traitement terminé."
            
            response_placeholder.markdown(response_text)
            
            # Affichage de la requête SQL si disponible
            if sql_query:
                st.markdown("---")
                st.markdown("**📝 Requête SQL générée :**")
                st.code(sql_query, language="sql")
            
            # Affichage de l'aperçu CSV
            if csv_path and os.path.exists(csv_path):
                st.markdown("---")
                st.markdown("**📊 Aperçu des données :**")
                df = pd.read_csv(csv_path)
                st.dataframe(df, use_container_width=True)
            
            # Affichage des visualisations
            if viz_path and os.path.exists(viz_path):
                st.markdown("---")
                st.markdown("**📈 Visualisation :**")
                st.image(viz_path, use_container_width=True)
            
            # Stockage des résultats pour l'historique
            results = {
                "csv_path": csv_path,
                "viz_path": viz_path,
                "sql_query": sql_query
            }
            
            # Générer un ID unique pour ce message
            msg_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            
            # Section téléchargement
            if csv_path or viz_path or sql_query:
                st.markdown("---")
                st.markdown("**📥 Téléchargements :**")
                st.markdown('<div class="download-section">', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if csv_path and os.path.exists(csv_path):
                    with open(csv_path, "rb") as f:
                        st.download_button(
                            label="📥 Télécharger CSV",
                            data=f,
                            file_name=os.path.basename(csv_path),
                            mime="text/csv",
                            use_container_width=True,
                            key=f"csv_{msg_id}"
                        )
            
            with col2:
                if viz_path and os.path.exists(viz_path):
                    with open(viz_path, "rb") as f:
                        st.download_button(
                            label="🖼️ Télécharger Image",
                            data=f,
                            file_name=os.path.basename(viz_path),
                            mime="image/png",
                            use_container_width=True,
                            key=f"img_{msg_id}"
                        )
            
            with col3:
                if sql_query:
                    st.download_button(
                        label="💾 Télécharger SQL",
                        data=sql_query,
                        file_name=f"query_{msg_id}.sql",
                        mime="text/plain",
                        use_container_width=True,
                        key=f"sql_{msg_id}"
                    )
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sauvegarde dans l'historique
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "tools": tools_used,
                "results": results,
                "msg_id": msg_id
            })
            
            # Scroll automatique vers le bas
            st.rerun()
            
        except Exception as e:
            error_msg = f"❌ **Erreur :** {str(e)}"
            response_placeholder.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "tools": tools_used
            })
            st.rerun()

