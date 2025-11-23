import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Assure-toi d'avoir ta clé API configurée
# os.environ["GOOGLE_API_KEY"] = "TA_CLE_API_GOOGLE_ICI"

def generate_sql_query(query_text):
    """Demande à Gemini de traduire le texte en SQL pour la boutique."""
    
    # On utilise 'gemini-1.5-flash' car il est rapide, pas cher et excellent en SQL
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
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
    - Utilise des JOINs si les informations sont dans plusieurs tables (ex: nom du produit + quantité en stock).
    - Renvoie UNIQUEMENT le code SQL brut. Ne mets PAS de balises markdown (```sql), pas d'introduction, pas d'explication.
    - Le code doit être prêt à être exécuté par cursor.execute().
    """
    
    response = llm.invoke(prompt)
    
    # Nettoyage de sécurité : on retire les balises markdown si l'IA en met quand même
    clean_sql = response.content.replace("```sql", "").replace("```", "").strip()
    
    return clean_sql

# --- Exemple d'utilisation pour tester ---
if __name__ == "__main__":
    # Test 1 : Demande simple
    question = "Combien de pulls avons-nous en stock au total ?"
    sql = generate_sql_query(question)
    print(f"Question : {question}")
    print(f"SQL généré : {sql}")
    
    print("-" * 20)

    # Test 2 : Demande complexe avec jointures
    question_complexe = "Donne-moi la liste des produits Zara (nom et prix) qui sont en taille M."
    sql_complexe = generate_sql_query(question_complexe)
    print(f"Question : {question_complexe}")
    print(f"SQL généré : {sql_complexe}")