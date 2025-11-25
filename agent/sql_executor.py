import sqlite3
import pandas as pd
import os
from datetime import datetime
from langchain_core.tools import tool  
from langchain_core.prompts import ChatPromptTemplate
@tool
def execute_and_export_sql( sql_query, output_format='csv')->str:
    """
    Exécute une requête SQL et exporte les résultats en CSV 
    
    Args:
        
        sql_query (str): Requête SQL à exécuter
        output_format (str): 'csv' 
        output_dir (str): Dossier où sauvegarder les exports dans mon projet dans le dossier exports
    
    Returns:
        str: Informations sur l'export
    """
    output_dir="exports"
    # Créer le dossier d'export s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect("data/boutique.db")
        
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
        
        return f"details {result_info}"
        
    except Exception as e:
        # 1. On crée le dictionnaire d'erreur proprement
        error_data = {
            'success': False,
            'error': str(e)
        }
        
        # 2. On le renvoie sous forme de chaîne (str)
        return f"Erreur : {error_data}"

