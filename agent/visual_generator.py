import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
from datetime import datetime
import numpy as np
from langchain_core.tools import tool  
from langchain_core.prompts import ChatPromptTemplate


def __init__(output_dir='visualizations'):
        """
        Initialise le générateur avec un style professionnel.
        """
        output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # --- Configuration Globale du Style ---
        # On essaie d'appliquer un style moderne, sinon on configure manuellement
        try:
            plt.style.use('seaborn-v0_8-whitegrid')
        except:
            plt.style.use('ggplot')

        colors = plt.cm.tab10.colors  # Palette de couleurs standard de haute qualité
        
        plt.rcParams.update({
            'font.size': 12,
            'font.family': 'sans-serif',
            'figure.autolayout': True, # Ajustement automatique des marges
            'axes.titlesize': 16,
            'axes.titleweight': 'bold',
            'axes.labelsize': 12,
            'figure.dpi': 150 # Meilleure résolution pour l'affichage
        })
@tool
def generate_visualization(csv_file_path, chart_type, title=None)->str:
    """
Génère un graphique visuel (PNG) à partir d'un fichier CSV donné.
Args:
    csv_file_path: Le chemin du fichier CSV.
    chart_type: Le type de graphique souhaité (Bar Charts, Pie Charts, Line Plots, Scatter Plots, Tableau).
Returns:
    Un message de succès avec le chemin de l'image.
"""
    print(f"DEBUG: Appel de l'outil Viz avec csv={csv_file_path} et type={chart_type}")
    try:
        # Lecture robuste du CSV
        df = pd.read_csv(csv_file_path)
        
        if df.empty:
            return {'success': False, 'error': 'Le fichier CSV est vide'}
        # Nettoyage basique : essayer de convertir les colonnes numériques si elles sont en string
        for col in df.columns:
            pd.to_numeric(df[col], errors='ignore')
        if not title:
            title = f"Analyse - {os.path.basename(csv_file_path)}"
        # Normalisation du type de chart
        ctype = chart_type.lower()
        
        if 'pie charts' in ctype:
            filepath = _create_donut_chart(df, title) # Upgrade vers Donut
        elif 'tableau' in ctype:
            filepath = _create_styled_table(df, title)
        elif 'line plots' in ctype:
            filepath = _create_line_plot(df, title)
        elif 'scatter plots' in ctype:
            filepath = _create_scatter_plot(df, title)
        elif 'bar charts' in ctype:
            filepath = _create_bar_chart(df, title)
        else:
            return {'success': False, 'error': f'Type non supporté: {chart_type}'}
        tmp={
            'success': True,
            'filepath': filepath,
            'chart_type': chart_type,
            'data_shape': df.shape,
            'columns': list(df.columns)
        }
        return  f"Graphique généré avec succès ici : {tmp}"
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"erreur {'success': False, 'error': str(e)}"
def _create_donut_chart(df, title):
    """Crée un Donut Chart (plus lisible qu'un Pie Chart classique)"""
    if len(df.columns) < 2:
        raise ValueError("Nécessite 2 colonnes (Labels, Valeurs)")
    
    labels = df.iloc[:, 0]
    values = df.iloc[:, 1]
    
    # Création de la figure
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Création du donut
    wedges, texts, autotexts = ax.pie(
        values, 
        labels=labels, 
        autopct='%1.1f%%', 
        startangle=90,
        pctdistance=0.85, # Pourcentage plus vers l'extérieur
        wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2), # L'anneau
        colors=plt.cm.Pastel1.colors
    )
    
    # Styliser le texte
    plt.setp(texts, size=10, fontweight="bold")
    plt.setp(autotexts, size=9, color="white", fontweight="bold")
    
    # Cercle blanc au centre (optionnel si wedgeprops width est utilisé, mais sécurise le look)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    
    ax.set_title(title, pad=20)
    ax.axis('equal')
    
    return _save_plot('donut')
def _create_bar_chart( df, title):
    """Crée un Bar Chart avec annotations de valeurs"""
    categories = df.iloc[:, 0].astype(str) # Force string pour x
    values = df.iloc[:, 1]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Barres avec une couleur unique mais esthétique
    bars = ax.bar(categories, values, color='#3498db', alpha=0.8, edgecolor='white', linewidth=1)
    
    ax.set_title(title, pad=20)
    ax.set_xlabel(df.columns[0])
    ax.set_ylabel(df.columns[1])
    
    # Rotation des labels si beaucoup de catégories
    if len(categories) > 5:
        plt.xticks(rotation=45, ha='right')
        
    # Grille horizontale seulement
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.grid(False)
    
    # Suppression des bordures inutiles (Haut et Droite)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Annotation des valeurs sur les barres
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2., 
            height,
            f'{height:,.0f}' if height > 100 else f'{height:.2f}', # Format intelligent
            ha='center', 
            va='bottom',
            fontsize=10,
            fontweight='bold',
            color='#444444'
        )
    
    return _save_plot('bar')
def _create_line_plot(df, title):
    """Crée un Line Plot multi-séries"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x_col = df.iloc[:, 0]
    
    # Tracer toutes les colonnes restantes comme des lignes
    for i, col in enumerate(df.columns[1:]):
        ax.plot(
            x_col, 
            df[col], 
            marker='o', 
            linewidth=2.5, 
            label=col,
            alpha=0.9
        )
    ax.set_title(title, pad=20)
    ax.set_xlabel(df.columns[0])
    ax.legend(frameon=True, fancybox=True, shadow=True)
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Si x contient beaucoup de points, on allège les labels
    if len(x_col) > 10:
         plt.xticks(rotation=45)
    return _save_plot('line')
def _create_scatter_plot( df, title):
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Ajout d'une dimension couleur si 3ème colonne existe
    c = df.iloc[:, 2] if len(df.columns) > 2 else None
    
    scatter = ax.scatter(
        df.iloc[:, 0], 
        df.iloc[:, 1], 
        c=c, 
        cmap='viridis' if c is not None else None,
        alpha=0.7, 
        s=100, 
        edgecolor='white'
    )
    
    if c is not None:
        plt.colorbar(scatter, label=df.columns[2])
    ax.set_title(title)
    ax.set_xlabel(df.columns[0])
    ax.set_ylabel(df.columns[1])
    ax.grid(True, linestyle=':', alpha=0.6)
    
    return _save_plot('scatter')
def _create_styled_table( df, title):
    """Crée un tableau rendu comme une image haute qualité"""
    fig, ax = plt.subplots(figsize=(12, len(df) * 0.5 + 2)) # Hauteur dynamique
    ax.axis('off')
    
    # Couleurs du tableau
    header_color = '#40466e'
    row_colors = ['#f1f1f2', 'w']
    edge_color = 'w'
    # Création du tableau
    table = ax.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='center',
        cellLoc='center'
    )
    
    # Styling avancé
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 1.8) # Plus d'espace vertical
    for k, cell in table.get_celld().items():
        cell.set_edgecolor(edge_color)
        if k[0] == 0: # Header
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else: # Rows
            cell.set_facecolor(row_colors[k[0]%len(row_colors)])
            
    plt.title(title, fontsize=16, weight='bold', pad=10)
    return _save_plot('table')
def _save_plot( chart_type):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{chart_type}_{timestamp}.png"
    filepath = os.path.join('visualizations', filename)
    # bbox_inches='tight' est crucial pour ne pas couper les légendes
    plt.savefig(filepath, dpi=200, bbox_inches='tight') 
    plt.close()
    return filepath

# --- Zone de Test ---
# Cette partie doit être désindentée (collée à la marge de gauche)
"""
if __name__ == "__main__":
    # 1. Instancier le générateur
    generator = VisualGenerator()

    # 2. Définir le chemin de ton fichier existant
    # J'ai ajouté le 'r' devant la chaîne pour gérer correctement les backslashes sous Windows
    csv_path = r"exports\export_20251124_203348.csv"

    # 3. Vérifier que le fichier existe avant de lancer
    if not os.path.exists(csv_path):
        print(f"⚠️ Fichier introuvable : {csv_path}")
        print("Assure-toi que le dossier 'exports' est bien au même endroit que ce script.")
    else:
        print(f"📂 Fichier trouvé : {csv_path}")
        print("🚀 Lancement de la génération des visuels améliorés...\n")

        # Liste des tests à effectuer
        test_scenarios = [
            ("Bar", "Analyse Stocks (Barres)"),
            ("Pie", "Répartition (Donut Chart)"),     
            ("Tableau", "Vue Tabulaire Stylisée"),   
            ("Line", "Tendances (Ligne)")
        ]

        for chart_type, title in test_scenarios:
            print(f"🎨 Génération de : {chart_type}...")
            
            result = generator.generate_visualization(
                csv_file_path=csv_path, 
                chart_type=chart_type, 
                title=title
            )
            
            if result['success']:
                print(f"   ✅ Succès ! Image sauvegardée ici : {result['filepath']}")
            else:
                print(f"   ❌ Erreur : {result['error']}")

        print("\n✨ Test terminé. Vérifie le dossier 'visualizations'.")
        """