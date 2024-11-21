import json
import pandas as pd
from pyvis.network import Network
import requests
from BERT.test import search_by_author, search_by_keyword, search_by_keyword_and_compare, find_similar_articles
from bs4 import BeautifulSoup
import os
import json
from sentence_transformers import SentenceTransformer, util
import numpy as np

def semantic_scholar_research(doi=None, title=None):
    """
    Utilise l'API de Semantic Scholar pour récupérer les informations sur une publication.
    """
    base_url = "https://api.semanticscholar.org/v1/paper/"
    if doi:
        response = requests.get(f"{base_url}{doi}")
    elif title:
        search_url = "https://api.semanticscholar.org/v1/paper/search"
        params = {"query": title}
        response = requests.get(search_url, params=params)
        if response.ok:
            search_results = response.json()
            if search_results['data']:
                paper_id = search_results['data'][0]['paperId']
                response = requests.get(f"{base_url}{paper_id}")
            else:
                return None, None, None, None, None, None, None, None
        else:
            return None, None, None, None, None, None, None, None
    else:
        return None, None, None, None, None, None, None, None

    if response.ok:
        data = response.json()
        title = data.get('title', None)
        abstract = data.get('abstract', None)
        authors = ', '.join([author['name'] for author in data.get('authors', [])])
        doi = data.get('doi', None)
        year = data.get('year', None)

        # Vérification des citations
        citations = data.get('citations', [])
        num_citations = len(citations)
        citation_dois = []

        # Récupérer les DOI des citations, s'ils existent
        for citation in citations:
            citation_doi = citation.get('doi', None)
            citation_dois.append(citation_doi if citation_doi else "DOI indisponible")
        
        # Si des citations ont été trouvées, retourne leur DOI
        doi_citations = citation_dois if citation_dois else ["Aucun DOI disponible"]
        url = data.get('url', None)

        # Retourne toujours 7 valeurs
        return title, abstract, authors, doi, year, num_citations, doi_citations, url
    else:
        return None, None, None, None, None, None, None, None


def cache(doi, title, abstract, authors, year, url, num_citations=0, doi_citations=None, cache_file='cache_doi.json'):
    if not os.path.exists(cache_file):
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)

    if doi:
        cache_data[doi] = {
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'year': year,
            'num_citations': num_citations,
            'doi_citations': doi_citations,
            'url': url
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=4)


def recuperate_data(csv_file='Bibliographie_mini.csv', cache_file='cache_doi.json'):
    # Charger le fichier CSV
    data = pd.read_csv(csv_file)
    
    # Initialiser les dictionnaires pour stocker les informations
    node_title = dict(zip(data['Title'], data['Title']))
    node_doi = dict(zip(data['Title'], data['DOI']))

    # Initialiser les variables pour stocker les citations et URL
    num_citations = 0
    doi_citations = {}
    url = ""

    # Charger le cache si disponible, sinon initialiser un cache vide
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
    else:
        cache_data = {}

    # Parcourir chaque ligne du CSV
    for index, row in data.iterrows():
        nom = row['Title']
        doi = node_doi[nom]

        # Vérification si DOI est une chaîne et s'il existe dans le cache
        if isinstance(doi, str) and doi.lower() in cache_data:
            num_citations = cache_data[doi.lower()]['num_citations']
            doi_citations = cache_data[doi.lower()]['doi_citations']
        elif isinstance(doi, str) and pd.notna(doi):
            # Appel à Semantic Scholar pour obtenir les informations si DOI est une chaîne et non NaN
            title, abstract, author, doi, year, num_citations, doi_citations, url = semantic_scholar_research(
                doi=doi,
                title=nom if pd.notna(nom) else None
            )

            # Si les informations sont manquantes, les valeurs par défaut sont utilisées
            title = title or "Titre inconnu"
            abstract = abstract or "Aperçu indisponible"
            author = author or "Auteur inconnu"
            doi = doi or "DOI indisponible"
            year = year or "Année inconnue"
            num_citations = num_citations if num_citations is not None else 0
            doi_citations = doi_citations or ["Pas de citations"]
            url = url or "URL indisponible"
            
            # Mettre à jour le cache
            if doi:
                cache(doi.lower(), title, abstract, author, year, url, num_citations, doi_citations)

    return data  # Retourne les données mises à jour du CSV (facultatif, selon l'utilisation)

#model = SentenceTransformer('TomDubois12/fine-tuned-model', token="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")
def load_or_compute_embeddings(model = SentenceTransformer('TomDubois12/fine-tuned-model', token="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"), embedding_file='cache_doi.json', title_weight=0.3, abstract_weight=0.7):
    """
    Charge les titres et résumés depuis un fichier JSON, génère les embeddings si nécessaires, et les ajoute au fichier.

    Args:
        model: SentenceTransformer utilisé pour calculer les embeddings.
        embedding_file: Nom du fichier JSON contenant les informations et dans lequel les embeddings seront ajoutés.
        title_weight: Pondération appliquée aux embeddings des titres.
        abstract_weight: Pondération appliquée aux embeddings des résumés.

    Returns:
        data: Dictionnaire des données enrichies avec les embeddings.
    """
    if not os.path.exists(embedding_file):
        raise FileNotFoundError(f"Le fichier '{embedding_file}' n'existe pas.")

    with open(embedding_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dois_to_process = []
    titles = []
    abstracts = []

    for doi, info in data.items():
        if "embeddings" not in info or "title" not in info["embeddings"] or "abstract" not in info["embeddings"]:
            title = info.get("title", "")
            abstract = info.get("abstract", "")
            if title or abstract:
                dois_to_process.append(doi)
                titles.append(title)
                abstracts.append(abstract)

    print("Calcul des embeddings pour les articles sans embeddings...")
    title_embeddings = model.encode(titles).tolist()
    abstract_embeddings = model.encode(abstracts).tolist()

    for doi, title_emb, abstract_emb in zip(dois_to_process, title_embeddings, abstract_embeddings):
        if "embeddings" not in data[doi]:
            data[doi]["embeddings"] = {}
        
        data[doi]["embeddings"]["title"] = title_emb
        data[doi]["embeddings"]["abstract"] = abstract_emb
        
        combined_embedding = title_weight * np.array(title_emb) + abstract_weight * np.array(abstract_emb)
        data[doi]["embeddings"]["combined"] = combined_embedding.tolist()

    with open(embedding_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data

if __name__ == "__main__":
    recuperate_data()
    load_or_compute_embeddings()