import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Charger le modèle pré-entraîné
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Charger le fichier CSV
df = pd.read_csv('Bibliographie.csv')

# Vérifier les premières lignes du DataFrame
print(df.head())

# Extraire les colonnes 'Key', 'Title', et 'Abstract Note'
keys = df['Key'].dropna().tolist()
titles = df['Title'].fillna('').tolist()  # Remplir les valeurs manquantes par des chaînes vides
abstracts = df['Abstract Note'].fillna('').tolist()

# Définir des pondérations pour le titre et l'abstract
title_weight = 0.3  # Poids du titre
abstract_weight = 0.7  # Poids de l'abstract

# Mot clé pour la recherche
mot_cle = "cycloaddition"

# Générer les embeddings pour les titres et les abstracts séparément
title_embeddings = model.encode(titles)
abstract_embeddings = model.encode(abstracts)
mot_cle_embedding = model.encode(mot_cle)

# Pondérer les embeddings
combined_embeddings = title_weight * title_embeddings + abstract_weight * abstract_embeddings

# Calculer la similarité entre le mot clé et chaque combinaison titre + abstract
similarities = util.cos_sim(mot_cle_embedding, combined_embeddings)

# Associer les similarités aux abstracts, titres et clés
similarities_with_title_abstracts = list(zip(keys, titles, abstracts, similarities[0].tolist()))

# Trier les résultats par ordre décroissant de similarité
similarities_with_title_abstracts.sort(key=lambda x: x[3], reverse=True)

# Afficher les 15 résultats les plus proches du mot clé avec leur Key, Titre et Abstract
print(f"Top 15 résultats pour le mot clé '{mot_cle}':\n")
for key, title, abstract, score in similarities_with_title_abstracts[:15]:
    print(f"Key: {key} \nTitle: {title} \nAbstract: {abstract} \nSimilarité: {score:.4f}\n")
