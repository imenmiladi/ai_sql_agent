from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from sql_executor import execute_and_export_sql
from sql_generator import generate_sql_query
from visual_generator import generate_visualization
import os
DB_PATH = "data/boutique.db"
EXPORT_DIR = "exports"
VIZ_DIR = "visualizations"
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(VIZ_DIR, exist_ok=True)

def create_agent():
    # 1. On donne les outils à l'agent
    tools = [generate_sql_query, execute_and_export_sql, generate_visualization]
    
    # 2. Le modèle principal
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # 3. Le Prompt Système (Le "Cerveau" qui décide quel outil appeler)
    prompt = ChatPromptTemplate.from_messages([
        ("system", 
         "Tu es un assistant Data Analyst expert."
         "Pour chaque demande :"
         "1. Utilise 'generate_sql_query' pour obtenir le SQL et le type de graphique ."
         "2. Parse le JSON reçu (si nécessaire)."
         "3. Utilise 'execute_sql_tool' avec le SQL. et utilise 'create_visualization_tool' avec le CSV et le type de graphique obtenu par generate_sql_query le titre du graphique doit etre significatif."
         "4. Réponds à l'utilisateur avec le résultat final et le chemin du graphique."
         ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    # verbose=True permet de voir le 'Reasoning' (Pensées) de l'agent dans la console
    return AgentExecutor(agent=agent, tools=tools, verbose=True)

# ==============================================================================
# TEST
# ==============================================================================
if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"⚠️ Attention : La base '{DB_PATH}' n'existe pas. Lance le script de création d'abord !")
    else:
        agent_executor = create_agent()
        
        print("\n--- TEST 1 : Question complexe ---")
        question = "Trouve les produits dont la composition contient du coton, triés par prix décroissant."
        
        try:
            result = agent_executor.invoke({"input": question})
            print(f"\n🤖 Réponse finale : {result['output']}")
        except Exception as e:
            print(f"Erreur : {e}")