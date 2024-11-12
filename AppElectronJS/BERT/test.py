import sys
import pandas as pd
import os
import json
import numpy as np  # NumPy pour manipuler les embeddings
from sentence_transformers import SentenceTransformer, util

# Configurer la sortie de la console pour utiliser l'UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def load_or_compute_embeddings(model, titles, abstracts, embedding_file='embeddings.json', title_weight=0.3, abstract_weight=0.7):
    """
    Charge les embeddings depuis un fichier JSON s'il existe ; sinon, calcule et stocke les embeddings dans un fichier.

    Args:
        model: SentenceTransformer utilisé pour calculer les embeddings.
        titles: Liste de titres des articles.
        abstracts: Liste de résumés des articles.
        embedding_file: Nom du fichier pour stocker/charger les embeddings.
        title_weight: Pondération appliquée aux embeddings des titres.
        abstract_weight: Pondération appliquée aux embeddings des résumés.

    Returns:
        combined_embeddings: Embeddings combinés des titres et résumés pondérés.
    """
    if os.path.exists(embedding_file):
        print("Chargement des embeddings depuis le fichier JSON...")
        with open(embedding_file, 'r', encoding='utf-8') as f:
            embeddings_data = json.load(f)
            title_embeddings = embeddings_data['title_embeddings']
            abstract_embeddings = embeddings_data['abstract_embeddings']
    else:
        print("Calcul et stockage des embeddings dans un fichier JSON...")
        title_embeddings = model.encode(titles).tolist()
        abstract_embeddings = model.encode(abstracts).tolist()
        with open(embedding_file, 'w', encoding='utf-8') as f:
            json.dump({
                'title_embeddings': title_embeddings,
                'abstract_embeddings': abstract_embeddings
            }, f)

    title_embeddings = np.array(title_embeddings, dtype=np.float32)
    abstract_embeddings = np.array(abstract_embeddings, dtype=np.float32)
    combined_embeddings = title_weight * title_embeddings + abstract_weight * abstract_embeddings

    return combined_embeddings

# Charger le modèle pré-entraîné
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1') #replacé plus tard par SentenceTransformer("fine_tuned_model")
df = pd.read_csv('./Data/Bibliographie_sans_doublon.csv', encoding='utf-8')
#df = pd.read_csv('Bibliographie_sans_doublon.csv', encoding='utf-8')
print(df.head())

keys = df['DOI'].tolist()
titles = df['Title'].fillna('').tolist()
abstracts = df['Abstract Note'].fillna('').tolist()
authors = df['Author'].fillna('').tolist()

combined_embeddings = load_or_compute_embeddings(model, titles, abstracts)

def search_by_keyword(mot_cle, nbNode):
    """
    Recherche les articles les plus similaires au mot-clé donné, basé sur la similarité cosinus des embeddings.

    Args:
        mot_cle: Mot-clé à rechercher.
        nbNode: Nombre d'articles les plus similaires à retourner.

    Returns:
        Liste de tuples (clé de l'article, score de similarité) pour les articles les plus similaires.
    """
    mot_cle_embedding = model.encode(mot_cle)
    similarities = util.cos_sim(mot_cle_embedding, combined_embeddings)
    similarities_with_title_abstracts = list(zip(keys, titles, abstracts, similarities[0].tolist()))
    similarities_with_title_abstracts.sort(key=lambda x: x[3], reverse=True)

    return [(t[0], t[3]) for t in similarities_with_title_abstracts[:nbNode]]

def search_by_keyword_and_compare(mot_cle):
    """
    Recherche les articles les plus similaires au mot-clé et calcule les similarités entre ces articles.

    Args:
        mot_cle: Mot-clé pour la recherche.

    Returns:
        Liste de tuples (clé1, clé2, similarité) représentant les similarités entre les articles du top 15.
    """
    mot_cle_embedding = model.encode(mot_cle)
    similarities = util.cos_sim(mot_cle_embedding, combined_embeddings)
    similarities_with_title_abstracts = list(zip(keys, titles, abstracts, combined_embeddings, similarities[0].tolist()))
    similarities_with_title_abstracts.sort(key=lambda x: x[4], reverse=True)

    top_15_results = similarities_with_title_abstracts[:5]
    embeddings_top_15 = np.array([embedding for _, _, _, embedding, _ in top_15_results])
    top_15_keys = [key for key, _, _, _, _ in top_15_results]
    similarity_matrix = util.cos_sim(embeddings_top_15, embeddings_top_15)

    similarities_list = []
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            similarities_list.append((top_15_keys[i], top_15_keys[j], similarity_matrix[i][j].item()))

    print("\nListe des similarités entre les articles du top 15 :")
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            print(f"Similarité entre {top_15_keys[i]} (article {i+1}) et {top_15_keys[j]} (article {j+1}): {similarity_matrix[i][j]:.4f}")

    return similarities_list

def find_similar_articles(key, x=5):
    """
    Trouve les x articles les plus similaires à un article donné par sa clé.

    Args:
        key: Clé de l'article de référence.
        x: Nombre d'articles similaires à retourner.

    Returns:
        Liste des x articles les plus similaires sous forme de tuples (clé de l'article, score de similarité).
    """
    if key not in keys:
        print(f"Aucun article trouvé avec la clé '{key}'.")
        return []

    article_index = keys.index(key)
    article_embedding = combined_embeddings[article_index]
    similarities = util.cos_sim(article_embedding, combined_embeddings)
    similarities_with_keys = list(zip(keys, similarities[0].tolist()))
    similarities_with_keys = sorted(similarities_with_keys, key=lambda x: x[1], reverse=True)
    similarities_with_keys = [item for item in similarities_with_keys if item[0] != key]

    return similarities_with_keys[:x]

def search_by_author(author_name):
    """
    Recherche les articles d'un auteur donné.

    Args:
        author_name: Nom de l'auteur pour la recherche.

    Returns:
        Liste des clés des articles de l'auteur.
    """
    author_name = author_name.lower()
    author_indices = [i for i, author in enumerate(authors) if author_name in author.lower()]

    if author_indices:
        print(f"Articles écrits par '{author_name}':\n")
        results = []
        for index in author_indices:
            key = keys[index]
            title = titles[index]
            author = authors[index]
            results.append((key, title, author))
            print(f"Key: {key} - Title: {title} - Author: {author}")
        return [key for key, _, _ in results]
    else:
        print(f"Aucun article trouvé pour l'auteur '{author_name}'.")
        return []

def search_by_title(title_keyword):
    """
    Recherche les articles contenant un mot-clé dans le titre.

    Args:
        title_keyword: Mot-clé de recherche dans le titre.

    Returns:
        Liste des clés des articles contenant le mot-clé dans le titre.
    """
    title_keyword = title_keyword.lower()
    title_indices = [i for i, title in enumerate(titles) if title_keyword in title.lower()]

    if title_indices:
        print(f"Articles contenant '{title_keyword}' dans le titre :\n")
        results = []
        for index in title_indices:
            key = keys[index]
            title = titles[index]
            author = authors[index]
            results.append((key, title, author))
            print(f"Key: {key} - Title: {title} - Author: {author}")
        return [key for key, _, _ in results]
    else:
        print(f"Aucun article trouvé avec le mot '{title_keyword}' dans le titre.")
        return []

print(search_by_title("Surface Modification and Oxygen Reduction on Glassy Carbon "))
