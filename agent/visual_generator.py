import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

class VisualGenerator:
    def __init__(self, output_dir='visualizations'):
        """
        Initialise le générateur de visualisations
        
        Args:
            output_dir (str): Dossier de sauvegarde des graphiques
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Configuration matplotlib pour le français
        plt.rcParams['font.size'] = 10
        plt.rcParams['figure.figsize'] = (12, 8)

    def generate_visualization(self, csv_file_path, chart_type, title=None):
        """
        Génère une visualisation à partir d'un fichier CSV
        
        Args:
            csv_file_path (str): Chemin vers le fichier CSV
            chart_type (str): Type de graphique ('pie', 'tableau', 'line', 'scatter', 'bar')
            title (str): Titre du graphique (optionnel)
        
        Returns:
            dict: Informations sur la visualisation générée
        """
        try:
            # Lecture du CSV
            df = pd.read_csv(csv_file_path)
            
            if df.empty:
                return {'success': False, 'error': 'Le fichier CSV est vide'}
            
            # Génération du titre si non fourni
            if not title:
                title = f"Visualisation - {os.path.basename(csv_file_path)}"
            
            # Sélection de la méthode de visualisation
            if chart_type.lower() == 'pie charts':
                filepath = self._create_pie_chart(df, title)
            elif chart_type.lower() == 'tableau':
                filepath = self._create_table(df, title)
            elif chart_type.lower() == 'line plots':
                filepath = self._create_line_plot(df, title)
            elif chart_type.lower() == 'scatter plots':
                filepath = self._create_scatter_plot(df, title)
            elif chart_type.lower() == 'bar':
                filepath = self._create_bar_chart(df, title)
            else:
                return {'success': False, 'error': f'Type de graphique non supporté: {chart_type}'}
            
            return {
                'success': True,
                'filepath': filepath,
                'chart_type': chart_type,
                'data_shape': df.shape,
                'columns': list(df.columns)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _create_pie_chart(self, df, title):
        """Crée un diagramme circulaire (Pie Chart)"""
        # On suppose que la première colonne est les labels et la seconde les valeurs
        if len(df.columns) < 2:
            raise ValueError("Le Pie Chart nécessite au moins 2 colonnes (labels et valeurs)")
        
        labels = df.iloc[:, 0]
        values = df.iloc[:, 1]
        
        plt.figure(figsize=(10, 8))
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.axis('equal')  # Assure que le pie chart est circulaire
        
        filepath = self._save_plot('pie')
        return filepath

    def _create_bar_chart(self, df, title):
        """Crée un diagramme en barres"""
        if len(df.columns) < 2:
            raise ValueError("Le Bar Chart nécessite au moins 2 colonnes (catégories et valeurs)")
        
        categories = df.iloc[:, 0]
        values = df.iloc[:, 1]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(categories, values, color='skyblue', alpha=0.7)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.xticks(rotation=45)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        filepath = self._save_plot('bar')
        return filepath

    def _create_line_plot(self, df, title):
        """Crée un graphique linéaire"""
        if len(df.columns) < 2:
            raise ValueError("Le Line Plot nécessite au moins 2 colonnes (x et y)")
        
        plt.figure(figsize=(12, 6))
        
        # Si plus de 2 colonnes, on trace plusieurs lignes
        if len(df.columns) == 2:
            plt.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o', linewidth=2)
        else:
            for col in df.columns[1:]:
                plt.plot(df.iloc[:, 0], df[col], marker='o', linewidth=2, label=col)
            plt.legend()
        
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(df.columns[0])
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filepath = self._save_plot('line')
        return filepath

    def _create_scatter_plot(self, df, title):
        """Crée un nuage de points"""
        if len(df.columns) < 2:
            raise ValueError("Le Scatter Plot nécessite au moins 2 colonnes (x et y)")
        
        plt.figure(figsize=(10, 6))
        plt.scatter(df.iloc[:, 0], df.iloc[:, 1], alpha=0.6, s=60)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(df.columns[0])
        plt.ylabel(df.columns[1])
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        filepath = self._save_plot('scatter')
        return filepath

    def _create_table(self, df, title):
        """Crée une visualisation de tableau"""
        plt.figure(figsize=(12, 8))
        plt.axis('off')
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Création du tableau
        table = plt.table(cellText=df.values,
                         colLabels=df.columns,
                         cellLoc='center',
                         loc='center',
                         bbox=[0, 0, 1, 0.9])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        filepath = self._save_plot('table')
        return filepath

    def _save_plot(self, chart_type):
        """Sauvegarde le graphique"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{chart_type}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()  # Ferme la figure pour libérer la mémoire
        return filepath

    def display_visualization_info(self, result_info):
        """Affiche les informations de la visualisation"""
        if not result_info['success']:
            print(f"❌ Erreur: {result_info['error']}")
            return
        
        print("✅ Visualisation créée avec succès!")
        print(f"📊 Type: {result_info['chart_type']}")
        print(f"📁 Fichier: {result_info['filepath']}")
        print(f"📈 Données: {result_info['data_shape'][0]} lignes × {result_info['data_shape'][1]} colonnes")
        print(f"🏷️ Colonnes: {', '.join(result_info['columns'])}")


# Fonction utilitaire pour un usage simple
def generate_visualization_from_csv(csv_file_path, chart_type, title=None):
    """
    Fonction simplifiée pour générer une visualisation
    
    Args:
        csv_file_path (str): Chemin vers le CSV
        chart_type (str): Type de graphique
        title (str): Titre optionnel
    
    Returns:
        dict: Résultat de la génération
    """
    generator = VisualGenerator()
    result = generator.generate_visualization(csv_file_path, chart_type, title)
    generator.display_visualization_info(result)
    return result


# Test du module
if __name__ == "__main__":
    # Test avec un fichier CSV exemple
    print("🧪 TEST DU VISUAL_GENERATOR")
    print("=" * 50)
    
    # Création d'un CSV de test
    test_data = {
        'Taille': ['S', 'M', 'L', 'XL'],
        'Pourcentage': [25.5, 35.2, 28.7, 10.6]
    }
    test_df = pd.DataFrame(test_data)
    test_df.to_csv('test_export.csv', index=False)
    
    # Test des différents types de graphiques
    test_cases = [
        ('test_export.csv', 'Pie Charts', 'Répartition des tailles en stock'),
        ('test_export.csv', 'Bar', 'Stock par taille'),
        ('test_export.csv', 'Line Plots', 'Évolution des stocks'),
        ('test_export.csv', 'Tableau', 'Tableau des stocks')
    ]
    
    for csv_file, chart_type, title in test_cases:
        print(f"\n📊 Test: {chart_type} - {title}")
        result = generate_visualization_from_csv(csv_file, chart_type, title)
        print("-" * 30)
    
    # Nettoyage
    if os.path.exists('test_export.csv'):
        os.remove('test_export.csv')