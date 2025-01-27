import os
import json
import re
import time
import requests
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


current_dir = os.path.dirname(os.path.abspath(__file__))
userSettingFile = os.path.join(current_dir, 'renderer/json/userSettings.json')
cache_file = os.path.join(current_dir, 'cache_doi.json')
Data = os.path.join(current_dir, 'Data/')
# Désactive les avertissements liés aux liens symboliques pour Hugging Face
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

def is_valid_doi(doi):
    """
    Vérifie si une chaîne de caractères correspond à un DOI valide.
    Exemple : 10.3895/recit.v5.n12.4301

    Args:
    - doi (str): La chaîne de caractères représentant un DOI.

    Returns:
    - bool: True si le DOI est valide, sinon False.
    """
    return bool(re.match(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", doi, re.IGNORECASE))

def is_valid_url(url):
    """
    Vérifie si une chaîne de caractères correspond à une URL valide de type Semantic Scholar.
    Exemple : https://www.semanticscholar.org/paper/Requirements-Engineering-for-Embedded-Systems%3A-A-Pereira-Ribeiro/d1f2f40c850d2c793ea6cbf13261824d53cfecee
    Args:
    - url (str): La chaîne de caractères représentant une URL.

    Returns:
    - bool: True si l'URL est valide, sinon False.
    """
    return bool(re.match(r'^https://www.semanticscholar.org/paper/', url))

def is_valid_url_doi(url_doi):
    """
    Vérifie si une chaîne de caractères correspond à un DOI valide.
    Exemple : https://doi.org/10.3895/recit.v5.n12.4301

    Args:
    - doi (str): La chaîne de caractères représentant un DOI.

    Returns:
    - bool: True si le DOI est valide, sinon False.
    """
    return bool(re.match(r"^https://doi\.org/10\.\d{4,9}/[-._;()/:A-Z0-9]+$", url_doi, re.IGNORECASE))

def get_response(doi_url):
    """
    Obtient la réponse de l'API Semantic Scholar en fonction du DOI ou de l'URL.

    Args:
    - doi_url (str): Le DOI ou l'URL d'un article.

    Returns:
    - response (requests.Response): La réponse de l'API, ou None si l'URL/DOI n'est pas valide.
    """
    base_url = "https://api.semanticscholar.org/v1/paper/"
    
    if is_valid_doi(doi_url):
        return requests.get(f"{base_url}{doi_url}")
    
    if is_valid_url(doi_url):
        paper_id = doi_url.split('/')[-1]
        return requests.get(f"{base_url}{paper_id}")

    if is_valid_url_doi(doi_url):
        doi_part = doi_url.split('https://doi.org/')[-1]  # Récupère tout après "https://doi.org/"
        return requests.get(f"{base_url}{doi_part}")
    
    return None

def extract_data_from_response(response):
    """
    Extrait les données pertinentes de la réponse JSON de l'API Semantic Scholar.

    Args:
    - response (requests.Response): La réponse de l'API.

    Returns:
    - tuple: Un tuple contenant les données extraites de l'article (titre, résumé, auteurs, DOI, année, 
             nombre de citations, DOI des citations, DOI des références, URL).
    """
    if response.ok:
        data = response.json()
        title = data.get('title')
        abstract = data.get('abstract')
        authors = ', '.join([author['name'] for author in data.get('authors', [])])
        doi = data.get('doi')
        year = data.get('year')
        citations = data.get('citations', [])
        references = data.get('references', [])

        num_citations = len(citations)

        citation_dois = []
        for citation in citations:
            if citation:
                citation_dois.append(citation.get('doi'))

        references_doi = []
        for reference in references:
            if references:
                references_doi.append(reference.get('doi'))

        return title, abstract, authors, doi, year, num_citations, citation_dois, references_doi, data.get('url')
    
    return None, None, None, None, None, None, None, None, None

def ajout_article(doi_url):
    """
    Récupère les informations d'un article à partir de son DOI ou URL et les met en cache.

    Args:
    - doi_url (str): Le DOI ou l'URL de l'article à récupérer.

    Returns:
    - str: Un message indiquant si l'article a été trouvé ou non.
    """
    response = get_response(doi_url)
    if response is None:
        return None
    title, abstract, authors, doi, year, num_citations, citation_dois, references_doi, url = extract_data_from_response(response)

    # Ajouter au cache
    cache(doi, title, abstract, authors, year, url, num_citations, citation_dois, references_doi)
    load_or_compute_embeddings()

def semantic_scholar_research(doi=None, title=None):
    """
    Recherche un article sur Semantic Scholar en utilisant le DOI ou le titre.

    Args:
    - doi (str, optional): Le DOI de l'article à rechercher. Par défaut None.
    - title (str, optional): Le titre de l'article à rechercher. Par défaut None.

    Returns:
    - tuple: Un tuple contenant les données extraites de l'article (titre, résumé, auteurs, DOI, année, 
             nombre de citations, DOI des citations, DOI des références, URL), ou None si l'article n'est pas trouvé.
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
                return None, None, None, None, None, None, None, None, None
        else:
            return None, None, None, None, None, None, None, None, None
    else:
        return None, None, None, None, None, None, None, None, None
    
    return extract_data_from_response(response)

def cache(doi, title, abstract, authors, year, url, num_citations=0, doi_citations=[], references_doi=[]):
    
    """
    Enregistre les informations sur un article dans un fichier de cache

    Args:
    - doi (str): Le DOI de l'article.
    - title (str): Le titre de l'article.
    - abstract (str): Le résumé de l'article.
    - authors (str): Les auteurs de l'article sous forme de chaîne.
    - year (str): L'année de publication de l'article.
    - url (str): L'URL de l'article.
    - num_citations (int, optional): Le nombre de citations de l'article. Par défaut 0.
    - doi_citations (list, optional): Les DOI des citations de l'article. Par défaut None.
    - references_doi (list, optional): Les DOI des références de l'article. Par défaut None.
    - cache_file (str, optional): Le nom du fichier où les données sont stockées. Par défaut 'cache_doi.json'.
    """

    # S'assurer que les paramètres ne sont pas None et utiliser les valeurs par défaut si nécessaire
    title = title if title is not None else "Titre inconnu"
    abstract = abstract if abstract is not None else "Aperçu indisponible"
    authors = authors if authors is not None else "Auteurs inconnus"
    year = year if year is not None else "Année inconnue"
    url = url if url is not None else "URL indisponible"
    num_citations = num_citations if num_citations is not None else 0
    doi_citations = doi_citations if doi_citations is not None else []
    references_doi = references_doi if references_doi is not None else []


    if not os.path.exists(cache_file):
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
        
    if doi and is_valid_doi(doi):
        cache_data[doi] = {
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'year': year,
            'num_citations': num_citations,
            'doi_references': references_doi,
            'url': url
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=4)

def recuperate_data():
    """
    Récupère les informations des articles à partir d'un fichier CSV et met à jour le cache.

    Args:
    - cache_file (str, optional): Le fichier de cache à mettre à jour. Par défaut 'cache_doi.json'.

    Returns:
    - pd.DataFrame: Les données du fichier CSV sous forme de DataFrame pandas, ou None si des erreurs sont rencontrées.
    """
    with open(userSettingFile, "r") as file:
        settings = json.load(file)
            
    csv_name = settings.get("CSVChoose", None)

    data = pd.read_csv(Data + csv_name)

    if 'DOI' not in data.columns:
        print("Erreur: Le fichier CSV ne contient pas de colonne 'DOI'")
        return None

    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
    else:
        cache_data = {}

    for index, row in data.iterrows():
        doi = row['DOI']
        if isinstance(doi, str) and doi.lower() in cache_data:
            # Si le DOI est dans le cache
            continue
        elif isinstance(doi, str) and pd.notna(doi):
            title, abstract, author, doi, year, num_citations, doi_citations, doi_references, url = semantic_scholar_research(doi=doi)

            title = title or "Titre inconnu"
            abstract = abstract or "Aperçu indisponible"
            author = author or "Auteur inconnu"
            doi = doi or "DOI indisponible"
            year = year or "Année inconnue"
            num_citations = num_citations if num_citations is not None else 0
            doi_citations = doi_citations or ["Pas de citations"]
            doi_references = doi_references or ["Pas de références"]
            url = url or "URL indisponible"

            cache(doi.lower(), title, abstract, author, year, url, num_citations, doi_citations, doi_references)

    return data

def load_or_compute_embeddings(model=SentenceTransformer('TomDubois12/fine-tuned-model', token="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"),
                               embedding_file=cache_file, title_weight=0.5, abstract_weight=0.5):
    """
    Charge les embeddings des titres et résumés et génère de nouveaux embeddings si nécessaire.

    Args:
    - model (SentenceTransformer, optional): Le modèle utilisé pour générer les embeddings. Par défaut un modèle pré-entraîné.
    - embedding_file (str, optional): Le fichier de cache contenant les embeddings. Par défaut 'cache_doi.json'.
    - title_weight (float, optional): Le poids attribué aux embeddings des titres. Par défaut 0.5.
    - abstract_weight (float, optional): Le poids attribué aux embeddings des résumés. Par défaut 0.5.

    Returns:
    - dict: Le dictionnaire contenant les embeddings des articles mis à jour.
    """
    if not os.path.exists(embedding_file):
        raise FileNotFoundError(f"Le fichier '{embedding_file}' n'existe pas.")

    with open(embedding_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    dois_to_process = []
    titles = []
    abstracts = []

    for doi, info in data.items():
        if "embeddings" not in info:
            dois_to_process.append(doi)
            titles.append(info.get("title", ""))
            abstracts.append(info.get("abstract", ""))

    print("Calcul des embeddings pour les articles sans embeddings...")
    title_embeddings = model.encode(titles).tolist()
    abstract_embeddings = model.encode(abstracts).tolist()

    for doi, title_emb, abstract_emb in zip(dois_to_process, title_embeddings, abstract_embeddings):
        if "embeddings" not in data[doi]:
            data[doi]["embeddings"] = {}

        if titles[dois_to_process.index(doi)] == "":
            title_emb = [0] * model.get_sentence_embedding_dimension()
        if abstracts[dois_to_process.index(doi)] == "":
            abstract_emb = [0] * model.get_sentence_embedding_dimension()

        data[doi]["embeddings"]["title"] = title_emb
        data[doi]["embeddings"]["abstract"] = abstract_emb

        combined_embedding = title_weight * np.array(title_emb) + abstract_weight * np.array(abstract_emb)
        data[doi]["embeddings"]["combined"] = combined_embedding.tolist()

    with open(embedding_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return data

if __name__ == "__main__":
    start_time = time.time()
    recuperate_data()
    end_time = time.time()
    print(f"Temps d'exécution de recuperate_data: {end_time - start_time:.2f} secondes")

    start_time = time.time()
    load_or_compute_embeddings()
    end_time = time.time()
    print(f"Temps d'exécution de load_or_compute_embeddings: {end_time - start_time:.2f} secondes")
