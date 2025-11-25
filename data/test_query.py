import sqlite3

# 1. Connexion à la base SQLite
db_path = "data/boutique.db"  # remplace par le chemin de ta base
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# 2. Écris ici ta requête SQL manuellement
sql_query = """

 SELECT taille, SUM(quantite_disponible) AS quantite_totale_pour_taille, (SUM(quantite_disponible) * 100.0 / (SELECT SUM(quantite_disponible) FROM stocks)) AS pourcentage_du_stock FROM stocks GROUP BY taille ORDER BY pourcentage_du_stock DESC;
    
    
"""

try:
    # 3. Exécution de la requête
    cursor.execute(sql_query)
    result = cursor.fetchall()
    
    # 4. Affichage du résultat
    for row in result:
        print(row)
except Exception as e:
    print("Erreur :", e)

# 5. Fermeture de la connexion
conn.close()




"""Question : Combien de pulls avons-nous en stock au total ?
SQL généré : SELECT SUM(S.quantite_disponible) FROM stocks AS S JOIN produits AS P ON S.produit_id = P.id WHERE P.nom_modele LIKE '%pull%';
--------------------
Question : Donne-moi la liste des produits Zara (nom et prix) qui sont en taille M.
SQL généré : SELECT
  p.nom_modele,
  p.prix_public
FROM produits AS p
JOIN marques AS m
  ON p.marque_id = m.id
JOIN stocks AS s
  ON p.id = s.produit_id
WHERE
  m.nom_marque = 'Zara' AND s.taille = 'M';
  
  
  
  
  Question : Combien de pulls avons-nous en stock au total ?
SQL généré : SELECT SUM(S.quantite_disponible)
FROM stocks AS S
JOIN produits AS P ON S.produit_id = P.id
JOIN categories AS C ON P.categorie_id = C.id
WHERE C.nom_categorie = 'Pull'
--------------------
Question : Donne-moi la liste des produits Zara (nom et prix) qui sont en taille M.
SQL généré : SELECT
  p.nom_modele,
  p.prix_public
FROM produits AS p
JOIN marques AS m
  ON p.marque_id = m.id
JOIN stocks AS s
  ON p.id = s.produit_id
WHERE
  m.nom_marque = 'Zara' AND s.taille = 'M';
  
  
  
Question : donne moi le pourcentage des tailles dans le stocks ?
WITH TotalStock AS (
    SELECT SUM(quantite_disponible) AS total_quantite
    FROM stocks
)
SELECT
    s.taille,
    (CAST(SUM(s.quantite_disponible) AS REAL) * 100.0 / (SELECT total_quantite FROM TotalStock)) AS pourcentage_taille
FROM
    stocks s
GROUP BY
    s.taille
ORDER BY
    pourcentage_taille DESC;
    
    SELECT taille, SUM(quantite_disponible) AS quantite_totale_pour_taille, (SUM(quantite_disponible) * 100.0 / (SELECT SUM(quantite_disponible) FROM stocks)) AS pourcentage_du_stock FROM stocks GROUP BY taille ORDER BY pourcentage_du_stock DESC;
"""

