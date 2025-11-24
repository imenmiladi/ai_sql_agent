import sqlite3
import pandas as pd
import os
from datetime import datetime

def execute_and_export_sql(db_path, sql_query, output_format='csv', output_dir='exports'):
    """
    Exécute une requête SQL et exporte les résultats en CSV ou Excel
    
    Args:
        db_path (str): Chemin vers la base de données SQLite
        sql_query (str): Requête SQL à exécuter
        output_format (str): 'csv' ou 'excel'
        output_dir (str): Dossier où sauvegarder les exports
    
    Returns:
        dict: Informations sur l'export
    """
    
    # Créer le dossier d'export s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        
        # Exécution de la requête et chargement dans un DataFrame pandas
        df = pd.read_sql_query(sql_query, conn)
        
        # Fermeture de la connexion
        conn.close()
        
        # Génération du nom de fichier avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format.lower() == 'csv':
            # Export en CSV (option recommandée)
            filename = f"export_{timestamp}.csv"
            filepath = os.path.join(output_dir, filename)
            df.to_csv(filepath, index=False, encoding='utf-8')
              
        else:
            raise ValueError("Format non supporté. ")
        
        # Retourner les informations de l'export
        result_info = {
            'success': True,
            'filepath': filepath,
            'filename': filename,
            'row_count': len(df),
            'columns': list(df.columns),
            'data_preview': df.head().to_dict('records')
        }
        
        return result_info
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def display_results(result_info):
    """
    Affiche les résultats de l'export de manière lisible
    """
    if not result_info['success']:
        print(f"❌ Erreur lors de l'exécution: {result_info['error']}")
        return
    
    print("✅ Export réalisé avec succès!")
    print(f"📁 Fichier: {result_info['filepath']}")
    print(f"📊 Nombre de lignes: {result_info['row_count']}")
    print(f"🏷️ Colonnes: {', '.join(result_info['columns'])}")
    
    # Aperçu des données
    if result_info['row_count'] > 0:
        print("\n👀 Aperçu des données (5 premières lignes):")
        preview_data = result_info['data_preview']
        for i, row in enumerate(preview_data, 1):
            print(f"  Ligne {i}: {row}")

# Fonction utilitaire pour traiter directement une question
def process_question(db_path, sql_query, question_text, output_format='csv'):
    """
    Traite une question complète : exécution SQL + export
    """
    print(f"\n{'='*60}")
    print(f"📋 QUESTION: {question_text}")
    print(f"🔍 SQL: {sql_query}")
    print(f"💾 Format d'export: {output_format.upper()}")
    print('='*60)
    
    # Exécution et export
    result = execute_and_export_sql(db_path, sql_query, output_format)
    
    # Affichage des résultats
    display_results(result)
    
    return result

# Exemple d'utilisation
if __name__ == "__main__":
    # Configuration
    DB_PATH = "data/boutique.db"
    
    # Exemple de requête SQL
    test_sql = """
    SELECT DISTINCT
      p.nom_modele,
      p.prix_public
    FROM produits AS p
    JOIN marques AS m
      ON p.marque_id = m.id
    JOIN stocks AS s
      ON p.id = s.produit_id
    WHERE
      m.nom_marque = 'Zara' AND s.taille = 'M'
    """
    
    # Traitement de la question
    process_question(
        db_path=DB_PATH,
        sql_query=test_sql,
        question_text="Donne-moi la liste des produits Zara (nom et prix) qui sont en taille M.",
        output_format='csv'
    )