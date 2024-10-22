import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Charger le modèle pré-entraîné
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

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

# Mot clé pour la recherche
mot_cle = "chimie"
nom_auteur = "Durant"  # Nom de l'auteur à rechercher

# Générer les embeddings pour les titres et les abstracts séparément
title_embeddings = model.encode(titles)
abstract_embeddings = model.encode(abstracts)
mot_cle_embedding = model.encode(mot_cle)

# Pondérer les embeddings
combined_embeddings = title_weight * title_embeddings + abstract_weight * abstract_embeddings

# Calculer la similarité entre le mot clé et chaque combinaison titre + abstract
similarities = util.cos_sim(mot_cle_embedding, combined_embeddings)

# Associer les similarités aux abstracts, titres, auteurs et clés
similarities_with_title_abstracts = list(zip(keys, titles, abstracts, authors, similarities[0].tolist()))

# Filtrer les résultats pour ne garder que ceux contenant le nom de l'auteur (insensible à la casse)
filtered_by_author = [item for item in similarities_with_title_abstracts if nom_auteur.lower() in item[3].lower()]

# Trier les résultats par ordre décroissant de similarité
filtered_by_author.sort(key=lambda x: x[4], reverse=True)

# Afficher les 15 résultats les plus proches du mot clé avec leur Key, Titre, Abstract et Auteur
print(f"Top résultats pour le mot clé '{mot_cle}' et l'auteur '{nom_auteur}':\n")
for key, title, abstract, author, score in filtered_by_author[:15]:
    print(f"Key: {key} \nTitle: {title} \nAbstract: {abstract} \nAuthor: {author} \nSimilarité: {score:.4f}\n")

# Si aucun auteur trouvé, afficher un message
if not filtered_by_author:
    print(f"Aucun résultat trouvé pour l'auteur '{nom_auteur}'.")
