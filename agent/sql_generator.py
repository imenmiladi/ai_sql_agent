import os
from dotenv import load_dotenv  
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. On charge les variables du fichier .env
load_dotenv()
def generate_sql_query(query_text):
    """Demande à Gemini de traduire le texte en SQL pour la boutique."""
    
    # On utilise 'gemini-1.5-flash' car il est rapide, pas cher et excellent en SQL
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    
    # On décrit précisément le schéma relationnel à l'IA
    schema_context = """
    Tables disponibles :
    1. categories (id, nom_categorie)
    2. marques (id, nom_marque, pays)
    3. produits (id, reference_interne, nom_modele, description, matiere_principale, composition, prix_public, genre, categorie_id, marque_id)
    4. stocks (id, produit_id, taille, couleur, quantite_disponible, emplacement_entrepot)

    Relations (Foreign Keys) :
    - produits.categorie_id -> categories.id
    - produits.marque_id -> marques.id
    - stocks.produit_id -> produits.id
    """
    
    prompt = f"""
    Tu es un expert SQL spécialisé dans SQLite.
    
    Voici le schéma de la base de données d'une boutique de vêtements :
    {schema_context}
    
    Tâche : Écris une requête SQL SQLite valide pour répondre à la demande suivante : "{query_text}".
    
    Consignes strictes :
    - utilise (DISTINCT, GROUP BY, HAVING, ORDER BY, LIMIT, JOIN,SUM, COUNT, AVG, MIN, MAX, etc) si nécessaire.
    - Applique les filtres implicites (taille, marque, couleur) si mentionnés dans la question.
    - Si la demande fait référence à une catégorie de produit (ex : "Pull", "Chaussure"), utilise la table categories et fais le JOIN approprié avec produits.
    - Utilise des JOINs si les informations sont dans plusieurs tables (ex: nom du produit + quantité en stock).
    - Renvoie une liste pour premier indice Renvoie UNIQUEMENT le code SQL brut. Ne mets PAS de balises markdown (```sql), pas d'introduction, pas d'explication.
    - Le code doit être prêt à être exécuté par cursor.execute() pour le deuxieme indice renvoie le type de graphique ideal (soit tableau,Line Plots,Pie Charts,Scatter Plots)
    """
    
    response = llm.invoke(prompt)
    
    # Nettoyage de sécurité : on retire les balises markdown si l'IA en met quand même
    clean_sql = response.content.replace("```sql", "").replace("```", "").strip()
    
    return clean_sql

# --- Exemple d'utilisation pour tester ---
if __name__ == "__main__":
    # Test 1 : Demande simple
    question = "donne moi le pourcentage des tailles dans le stocks ?"
    sql = generate_sql_query(question)
    print(f"Question : {question}")
    print(f"SQL généré : {sql}")
    
    
    print("-" * 20)

    # Test 2 : Demande complexe avec jointures
    question_complexe = "Donne-moi la liste des produits Zara (nom et prix) qui sont en taille M."
    sql_complexe = generate_sql_query(question_complexe)
    print(f"Question : {question_complexe}")
    print(f"SQL généré : {sql_complexe}")