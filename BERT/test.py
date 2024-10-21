import pandas as pd
import os
import json
import numpy as np  # NumPy pour manipuler les embeddings
from sentence_transformers import SentenceTransformer, util

# Charger le modèle pré-entraîné
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')

# Charger le fichier CSV
df = pd.read_csv('Bibliographie.csv')

# Vérifier les premières lignes du DataFrame
print(df.head())

# Extraire les colonnes 'Key', 'Title', 'Abstract Note' et 'Author'
keys = df['Key'].dropna().tolist()
titles = df['Title'].fillna('').tolist()  # Remplir les valeurs manquantes par des chaînes vides
abstracts = df['Abstract Note'].fillna('').tolist()
authors = df['Author'].fillna('').tolist()  # Remplir les valeurs manquantes par des chaînes vides

# Définir des pondérations pour le titre et l'abstract
title_weight = 0.3  # Poids du titre
abstract_weight = 0.7  # Poids de l'abstract

# Chemin vers le fichier JSON où les embeddings seront stockés
embedding_file = 'embeddings.json'

# Vérifier si les embeddings sont déjà stockés dans le fichier JSON
if os.path.exists(embedding_file):
    print("Chargement des embeddings depuis le fichier JSON...")
    with open(embedding_file, 'r') as f:
        embeddings_data = json.load(f)
        title_embeddings = embeddings_data['title_embeddings']
        abstract_embeddings = embeddings_data['abstract_embeddings']
else:
    print("Calcul et stockage des embeddings dans un fichier JSON...")
    # Calculer les embeddings pour les titres et abstracts
    title_embeddings = model.encode(titles).tolist()  # Convertir en liste pour pouvoir les stocker en JSON
    abstract_embeddings = model.encode(abstracts).tolist()

    # Stocker les embeddings dans un fichier JSON
    with open(embedding_file, 'w') as f:
        json.dump({
            'title_embeddings': title_embeddings,
            'abstract_embeddings': abstract_embeddings
        }, f)

# Convertir les embeddings de listes en tableaux NumPy (et assurer un dtype cohérent)
title_embeddings = np.array(title_embeddings, dtype=np.float32)  # Conversion en float32
abstract_embeddings = np.array(abstract_embeddings, dtype=np.float32)  # Conversion en float32

# Pondérer les embeddings
combined_embeddings = title_weight * title_embeddings + abstract_weight * abstract_embeddings

# Fonction de recherche par mot clé
def search_by_keyword(mot_cle):
    mot_cle_embedding = model.encode(mot_cle)

    # Calculer la similarité entre le mot clé et chaque combinaison titre + abstract
    similarities = util.cos_sim(mot_cle_embedding, combined_embeddings)

    # Associer les similarités aux articles
    similarities_with_title_abstracts = list(zip(keys, titles, abstracts, similarities[0].tolist()))

    # Trier les résultats par ordre décroissant de similarité
    similarities_with_title_abstracts.sort(key=lambda x: x[3], reverse=True)

    # Afficher les 15 résultats les plus proches du mot clé avec leur Key, Titre et Abstract
    print(f"Top 15 résultats pour le mot clé '{mot_cle}':\n")
    for key, title, abstract, score in similarities_with_title_abstracts[:15]:
        print(f"Key: {key} \nTitle: {title} \nAbstract: {abstract} \nSimilarité: {score:.4f}\n")

# Fonction de recherche par auteur
def search_by_author(author_name):
    # Mettre l'auteur en minuscules pour une recherche insensible à la casse
    author_name = author_name.lower()
    
    # Trouver les keys des articles écrits par l'auteur
    author_keys = [key for key, author in zip(keys, authors) if author_name in author.lower()]

    if author_keys:
        print(f"Articles écrits par '{author_name}':\n")
        for key in author_keys:
            print(f"Key: {key}")
    else:
        print(f"Aucun article trouvé pour l'auteur '{author_name}'.")

# Exemple d'utilisation
mot_cle = "Linear sweep voltammetry at very small stationary disk electrodes"
search_by_keyword(mot_cle)

author_name = "John F"
search_by_author(author_name)
