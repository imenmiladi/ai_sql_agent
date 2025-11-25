import sqlite3
import os

db_file = "data/boutique.db"

if os.path.exists(db_file):
    os.remove(db_file)

conn = sqlite3.connect(db_file)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

print("Création des tables relationnelles...")

# 1. Table CATEGORIES
cursor.execute('''
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_categorie TEXT NOT NULL UNIQUE -- Ex: 'Pull', 'Jean', 'Chemise'
);
''')

# 2. Table MARQUES
cursor.execute('''
CREATE TABLE marques (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_marque TEXT NOT NULL UNIQUE,
    pays TEXT
);
''')

# 3. Table PRODUITS 
cursor.execute('''
CREATE TABLE produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_interne TEXT UNIQUE,
    nom_modele TEXT NOT NULL,
    description TEXT,
    matiere_principale TEXT,      -- Ex: Laine
    composition TEXT,             -- Ex: 100% Coton
    prix_public REAL,
    genre TEXT,                   -- Homme/Femme/Unisexe
    categorie_id INTEGER,
    marque_id INTEGER,
    FOREIGN KEY (categorie_id) REFERENCES categories(id),
    FOREIGN KEY (marque_id) REFERENCES marques(id)
);
''')

# 4. Table STOCKS 
cursor.execute('''
CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produit_id INTEGER,
    taille TEXT NOT NULL,         -- S, M, L, 42, 44...
    couleur TEXT NOT NULL,
    quantite_disponible INTEGER DEFAULT 0,
    emplacement_entrepot TEXT,    -- Ex: 'Etagere A1'
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);
''')

# --- SEEDING (Remplissage) ---

print("Injection des données...")

# A. Catégories
cats = [('Pull',), ('Pantalon',), ('Veste',), ('Accessoire',)]
cursor.executemany("INSERT INTO categories (nom_categorie) VALUES (?)", cats)

# B. Marques
brands = [('Zara', 'Espagne'), ('Uniqlo', 'Japon'), ('Levi\'s', 'USA'), ('H&M', 'Suède')]
cursor.executemany("INSERT INTO marques (nom_marque, pays) VALUES (?, ?)", brands)

# Récupération des ID pour les liaisons
cursor.execute("SELECT id, nom_categorie FROM categories")
cat_map = {nom: id for id, nom in cursor.fetchall()} # {'Pull': 1, 'Pantalon': 2...}

cursor.execute("SELECT id, nom_marque FROM marques")
brand_map = {nom: id for id, nom in cursor.fetchall()}

# C. Produits (Catalogue)
produits_data = [
    # ref, nom, desc, matiere, compo, prix, genre, cat_id, brand_id
    ('P001', 'Pull Col V Mérinos', 'Pull fin classique', 'Laine', '100% Mérinos', 49.90, 'Homme', cat_map['Pull'], brand_map['Uniqlo']),
    ('P002', 'Sweat Oversize', 'Sweat à capuche street', 'Coton', '80% Coton, 20% Poly', 35.00, 'Unisexe', cat_map['Pull'], brand_map['H&M']),
    ('J001', 'Jean 501 Original', 'Le classique indémodable', 'Denim', '100% Coton', 99.00, 'Homme', cat_map['Pantalon'], brand_map['Levi\'s']),
    ('P003', 'Pull Torsadé Hiver', 'Grosse maille chaude', 'Laine', '50% Laine, 50% Acrylique', 59.95, 'Femme', cat_map['Pull'], brand_map['Zara'])
]

cursor.executemany('''
    INSERT INTO produits (reference_interne, nom_modele, description, matiere_principale, composition, prix_public, genre, categorie_id, marque_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', produits_data)

# D. Stocks (Variantes Taille/Couleur)
# On doit récupérer les ID des produits qu'on vient de créer
cursor.execute("SELECT id, reference_interne FROM produits")
prod_map = {ref: id for id, ref in cursor.fetchall()}

stocks_data = [
    # Le Pull Mérinos (P001) existe en plusieurs variantes
    (prod_map['P001'], 'M', 'Gris', 10, 'A1'),
    (prod_map['P001'], 'L', 'Gris', 5, 'A1'),
    (prod_map['P001'], 'M', 'Bleu Marine', 8, 'A2'),
    (prod_map['P001'], 'XL', 'Bleu Marine', 2, 'A2'),
    
    # Le Sweat H&M (P002)
    (prod_map['P002'], 'S', 'Noir', 20, 'B1'),
    (prod_map['P002'], 'M', 'Noir', 15, 'B1'),
    
    # Le Jean Levi's (J001) - Tailles américaines
    (prod_map['J001'], '30/32', 'Bleu Stone', 12, 'C1'),
    (prod_map['J001'], '32/32', 'Bleu Stone', 8, 'C1'),
    
    # Le Pull Zara (P003)
    (prod_map['P003'], 'S', 'Écru', 6, 'D4'),
    (prod_map['P003'], 'M', 'bleu', 6, 'D4'),
    (prod_map['P003'], 'M', 'Écru', 0, 'D4') # Rupture de stock pour tester l'IA
]

cursor.executemany('''
    INSERT INTO stocks (produit_id, taille, couleur, quantite_disponible, emplacement_entrepot)
    VALUES (?, ?, ?, ?, ?)
''', stocks_data)

conn.commit()
print("Base de données 'boutique_complexe.db' générée avec succès.")

# Test visuel : Jointure pour voir l'inventaire complet
print("\n--- TEST : Inventaire complet (Vue humaine) ---")
sql_test = '''
SELECT 
    m.nom_marque, 
    p.nom_modele, 
    s.couleur, 
    s.taille, 
    s.quantite_disponible 
FROM stocks s
JOIN produits p ON s.produit_id = p.id
JOIN marques m ON p.marque_id = m.id
WHERE p.categorie_id = (SELECT id FROM categories WHERE nom_categorie = 'Pull')
'''
cursor.execute(sql_test)
for row in cursor.fetchall():
    print(f"{row[0]} - {row[1]} ({row[2]}, {row[3]}) : {row[4]} en stock")

conn.close()