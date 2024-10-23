import pandas as pd
import os
import json
import numpy as np  # NumPy pour manipuler les embeddings
from sentence_transformers import SentenceTransformer, util

def load_or_compute_embeddings(model, titles, abstracts, embedding_file='embeddings.json', title_weight=0.3, abstract_weight=0.7):
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

    return combined_embeddings

# Charger le modèle pré-entraîné
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')

# Charger le fichier CSV
df = pd.read_csv('BERT/Bibliographie.csv')

# Vérifier les premières lignes du DataFrame
print(df.head())

# Extraire les colonnes 'Key', 'Title', 'Abstract Note' et 'Author'
keys = df['Key'].dropna().tolist()
titles = df['Title'].fillna('').tolist()  # Remplir les valeurs manquantes par des chaînes vides
abstracts = df['Abstract Note'].fillna('').tolist()
authors = df['Author'].fillna('').tolist()  # Remplir les valeurs manquantes par des chaînes vides

# Utiliser la fonction pour charger ou calculer les embeddings
combined_embeddings = load_or_compute_embeddings(model, titles, abstracts)


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
    return [(t[0], t[3]) for t in similarities_with_title_abstracts[:15]]

# Fonction de recherche par mot clé avec calcul de la similarité entre les résultats
def search_by_keyword_and_compare(mot_cle):
    mot_cle_embedding = model.encode(mot_cle)

    # Calculer la similarité entre le mot clé et chaque combinaison titre + abstract
    similarities = util.cos_sim(mot_cle_embedding, combined_embeddings)

    # Associer les similarités aux articles
    similarities_with_title_abstracts = list(zip(keys, titles, abstracts, combined_embeddings, similarities[0].tolist()))

    # Trier les résultats par ordre décroissant de similarité
    similarities_with_title_abstracts.sort(key=lambda x: x[4], reverse=True)

    # Extraire les embeddings et keys des 15 articles les plus proches du mot clé
    top_15_results = similarities_with_title_abstracts[:15]
    embeddings_top_15 = np.array([embedding for _, _, _, embedding, _ in top_15_results])
    top_15_keys = [key for key, _, _, _, _ in top_15_results]

    # Calculer la similarité entre les articles du top 15
    similarity_matrix = util.cos_sim(embeddings_top_15, embeddings_top_15)

    # Créer une liste pour stocker les similarités entre les articles
    similarities_list = []

    # Ajouter les similarités sous forme (key1, key2, similarité)
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):  # Eviter la redondance des comparaisons
            similarities_list.append((top_15_keys[i], top_15_keys[j], similarity_matrix[i][j].item()))

    # Afficher les 15 résultats les plus proches du mot clé
    print(f"Top 15 résultats pour le mot clé '{mot_cle}':\n")
    for idx, (key, title, abstract, _, score) in enumerate(top_15_results, 1):
        print(f"Key: {key} \nTitle: {title} \nAbstract: {abstract} \nSimilarité: {score:.4f}\n")

    # Afficher la liste des similarités entre les articles du top 15 avec les indices (i, j)
    print("\nListe des similarités entre les articles du top 15 :")
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            print(f"Similarité entre {top_15_keys[i]} (article {i+1}) et {top_15_keys[j]} (article {j+1}): {similarity_matrix[i][j]:.4f}")

    return similarities_list


# Fonction pour trouver les x articles les plus similaires à un article donné par sa clé
def find_similar_articles(key, x=5):
    # Trouver l'index de l'article correspondant à la clé donnée
    if key not in keys:
        print(f"Aucun article trouvé avec la clé '{key}'.")
        return []

    article_index = keys.index(key)
    article_embedding = combined_embeddings[article_index]

    # Calculer la similarité entre l'article donné et tous les autres articles
    similarities = util.cos_sim(article_embedding, combined_embeddings)

    # Associer chaque article à son score de similarité
    similarities_with_keys = list(zip(keys, similarities[0].tolist()))

    # Trier les articles par ordre décroissant de similarité, sauf l'article lui-même (index != article_index)
    similarities_with_keys = sorted(similarities_with_keys, key=lambda x: x[1], reverse=True)

    # Retirer l'article lui-même de la liste
    similarities_with_keys = [item for item in similarities_with_keys if item[0] != key]

    # Retourner les x articles les plus similaires sous forme de liste
    return similarities_with_keys[:x]


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


mot_cle = "Linear sweep voltammetry at very small stationary disk electrodes"
similarities = search_by_keyword_and_compare(mot_cle)


article_key = "Z7PHWZU3"
x = 5
similar_articles = find_similar_articles(article_key, x)  # Trouver les 5 articles les plus similaires
print("--------------------------------------------")
print(f"Les {x} articles les plus proches de l'article {article_key}")
print(similar_articles)
print("--------------------------------------------")


author_name = "John F"
print("--------------------------------------------")
search_by_author(author_name)
print("--------------------------------------------")