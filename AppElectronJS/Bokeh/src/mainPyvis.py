import json
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network
import requests
from BERT.test import search_by_author, search_by_keyword, search_by_keyword_and_compare, find_similar_articles
import sys
from bs4 import BeautifulSoup
import os
import json
import math

def ajout_script(network):
    # Add custom script for handling node clicks and displaying the publication title
    custom_script = """
    <div id="result"></div>
    <script type="text/javascript" src="Bokeh/bin/lib/binding/utils.js"></script>
    <script src="js/EventNodeEdge.js"> </script>
    """
    return custom_script

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


def recuperate_data(csv_file, cache_file='cache_doi.json'):
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

        if doi.lower() in cache_data:
            num_citations = cache_data[doi.lower()]['num_citations']
            doi_citations = cache_data[doi.lower()]['doi_citations']
        else:
            # Appel à Semantic Scholar pour obtenir les informations
            title, abstract, author, doi, year, num_citations, doi_citations, url = semantic_scholar_research(
                doi=doi if pd.notna(doi) else None,
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

def get_list_xSimilaritie(listeKey, x=1):
    """
    Take a liste of key, for exemple 15 key similar from the keyWords and return a list of x similar article for each key.
    return a list of list with 2 element, first: the key. second: a list of key of x article similar 
    """
    liste_final = []
    for key in listeKey:
        listeSimiliarities = find_similar_articles(key, x)
        liste_final += [[key, [(t[0],t[1]) for t in listeSimiliarities]]]
    return liste_final


def getDataFrame(dataUser):
    file = dataUser["pathDirectoryCSV"] +"/"+ dataUser["CSVChoose"]
    data = pd.read_csv(file)
    df = data.iloc[:, [0,1,2,3,4,5,6,7,8,9,10,11, -1]] #rajout de la colonne nbCitation avec le -1 

    # Définir la colonne "DOI" comme index
    df.set_index("DOI", inplace=True)
    return df


def setLiaison(G, liaison, allTheKeys, listeKeys, dfFinal, noms, infos):
    match liaison['liaisonName']:
        case 'Similarité':
            # Add the edges
            for key, keys in listeKeys:
                for key2 in keys:
                    G.add_edge(key, key2[0],length=(500 - ((key2[1] - 0.7) / (1 - 0.7)) * (500 - 20)), color=liaison['color'])
        case 'Citation':
                cache_file = 'cache_doi.json'
                if os.path.exists(cache_file):
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                else:
                    cache_data = {}  # Si le fichier n'existe pas, initialiser un cache vide
                allTheKeys = set(allTheKeys)
                set_liaison_final = set()
                for key in allTheKeys:
                    if key.lower() in cache_data.keys():
                        key = key.lower()
                    if key.upper() in cache_data.keys():
                        key = key.upper()
                    print(key)
                    liste_doi = cache_data[key]["doi_citations"]
                    for keyCite in liste_doi:
                        if keyCite in allTheKeys:
                            set_liaison_final.add((keyCite, key))
                print(set_liaison_final)
                for couple in set_liaison_final:
                    G.add_edge(couple[0],couple[1], color=liaison['color'])

        case 'Date de publication':
            result = {
                year: tuple(group.index.unique()) for year, group in dfFinal.groupby('Publication Year')
            }
            for year in result:
                listeKeyYear = result[year]
                for i in range(len(listeKeyYear)-1):
                    for j in range(i+1,len(listeKeyYear)):
                        G.add_edge(listeKeyYear[i], listeKeyYear[j], color=liaison['color'])
    return G


def find_min_max_values(dico,noms):
    liste = set()
    for nom in noms:
        if(nom in dico.keys()):
            liste.add(dico[nom.lower()]['num_citations'])

    #return the min and max of a dico like this {"DOI": nbCitation}
    min_key = min(liste)
    max_key = max(liste)
    return min_key, max_key


def transform_value_log(value, original_min, original_max, target_min=20, target_max=100):
    # Ajouter une petite valeur epsilon pour éviter le log de 0
    epsilon = 1e-6
    
    # Normaliser la valeur par rapport à la plage originale
    normalized_value = (value - original_min) / (original_max - original_min)
    
    # Appliquer une transformation logarithmique pour donner plus de différenciation aux petites valeurs
    log_transformed = math.log1p((normalized_value ** 0.9) * (math.e - 1))  # log1p(x) = log(1 + x) pour éviter les problèmes autour de 0
    
    # Transformation linéaire vers la plage cible
    transformed_value = target_min + log_transformed * (target_max - target_min)
    print(transformed_value)
    return transformed_value


def show_graphique(liste_key, dataUser):
    """
        liste_key: list of list [[onePrincipaleKey, [(childKey1, similaritieWithParent), (...)]]]
    """
    def getListallKey(liste_key):
        """return:
            allTheKeys: (List): A list of all the OriginKeys + all the ChildKeys
            originKeys: (List): A list of all the OriginKeys
            childKeys:  (List): A list of all the ChildKeys
        """  
        all_key1 = [t[0] for t in liste_key] #List of originNode, the node with the more similarities with the subject.
        all_key2 = [t[1] for t in liste_key] #List of the childs of all the originNode.
        all_key2 = [t[0] for _t in all_key2 for t in _t]

        return all_key1+all_key2, all_key1, all_key2
    
    def setAllNode(G,noms,infos):
        recuperate_data(dfFinal, noms, infos)
        cache_file = 'cache_doi.json'

        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

       

        # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        minTaille, maxTaille = find_min_max_values(cache_data, noms)
        
            # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        for nom in noms:
            if(nom.lower() in cache_data.keys()):
                node = cache_data[nom.lower()]
                nodeTaille = transform_value_log(node['num_citations'], minTaille, maxTaille)
                color = 'red' if nom in originKeys else 'blue'  # Red for origin nodes, blue otherwise
        
                G.add_node(
                    nom,
                    size=nodeTaille,
                    label=node['authors'].split(",")[0] +" "+ str(node['year']),
                    year=node['year'],
                    title=node['title'],
                    abstract=node['abstract'],
                    author=node['authors'],
                    doi=nom,
                    color=color,
                    nb_citations=node['num_citations'],
                    citations=node['doi_citations'],
                    url=node['url'],
                    isOrigin=nom in originKeys
                )
        return G
    
    # Create the graph
    G = nx.Graph()
    #Get the df, the file for the CSV is directly in the function
    df = getDataFrame(dataUser)
    
    # Reindexer le DataFrame selon les clés trouvées
    allTheKeys, originKeys, childKeys = getListallKey(liste_key)
    dfFinal = df.reindex(allTheKeys)

    noms = dfFinal.index  # Use the index (the keys)
    infos = dfFinal.iloc[:, 0:3]  # Take the columns that contain the information
    
    originKeys = set(originKeys)#Transform the list in a set for faster reserch in the list

    G = setAllNode(G,noms,infos)


    liaisons = dataUser["ColorPickerSettings"]

    for liaison in liaisons:
        if liaison['check'] == 'true':
            G = setLiaison(G, liaison, allTheKeys, liste_key, dfFinal, noms, infos)

    nt = Network('100vh', '100vw', notebook=True)
    # nt.show_buttons(filter_=['physics'])
    nt.from_nx(G)

    # Create the HTML file
    html_file_path = 'Bokeh/bin/nx.html'
    nt.save_graph(html_file_path)

    # Manually modify the HTML to include the JavaScript functionality
    with open(html_file_path, 'r') as f:
        html_content = f.read()
    
    # Insert the custom script just before the closing </body> tag
    html_content = html_content.replace('</body>', ajout_script( nt) + '</body>')

    # Write the modified content back to the file
    with open(html_file_path, 'w') as f:
        f.write(html_content)



def show_graphique_author(liste_key):

    def setAllNode(G,noms,infos):
        recuperate_data(dfFinal, noms, infos)
        cache_file = 'cache_doi.json'

        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

       

        # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        minTaille, maxTaille = find_min_max_values(cache_data, noms)
        
            # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        for nom in noms:
            node = cache_data[nom.lower()]
            nodeTaille = transform_value_log(node['num_citations'], minTaille, maxTaille)
            color = 'red' if nom in originKeys else 'blue'  # Red for origin nodes, blue otherwise
            print(node['authors'])
            G.add_node(
                nom,
                size=nodeTaille,
                label=node['authors'].split(",")[0] +" "+ str(node['year']),
                year=node['year'],
                title=node['title'],
                abstract=node['abstract'],
                author=node['authors'],
                doi=nom,
                color=color,
                nb_citations=node['num_citations'],
                citations=node['doi_citations'],
                url=node['url'],
                isOrigin=nom in originKeys
            )
        return G

    # Create the graph
    G = nx.Graph()

    #Get the df, the file for the CSV is directly in the function
    df = getDataFrame(dataUser)
    
    # Reindexer le DataFrame selon les clés trouvées
    allTheKeys = liste_key
    dfFinal = df.reindex(allTheKeys)
    
    noms = dfFinal.index  # Use the index (the keys)
    infos = dfFinal.iloc[:, 0:3]  # Take the columns that contain the information
    
    originKeys = set(allTheKeys)  # Take the 15 keys from liste_key

    G = setAllNode(G,noms,infos)

    liaisons = dataUser["ColorPickerSettings"]

    liste_cle1_cle2 = []    
    for key in liste_key:
        articles_similaire = find_similar_articles(key, 3)
        newList = [key]
        tempList = []
        for elem in articles_similaire:
            if elem[0] in liste_key:
                tempList.append(elem)
        newList.append(tempList)
        liste_cle1_cle2.append(newList)
    for liaison in liaisons:
        if liaison['check'] == 'true':
            G = setLiaison(G, liaison, allTheKeys, liste_cle1_cle2, dfFinal, noms, infos)


    nt = Network('100vh', '100vw', notebook=True)
    # nt.show_buttons(filter_=['physics'])
    nt.from_nx(G)

    # Create the HTML file
    html_file_path = 'Bokeh/bin/nx.html'
    nt.save_graph(html_file_path)

    # Manually modify the HTML to include the JavaScript functionality
    with open(html_file_path, 'r') as f:
        html_content = f.read()
    
    # Insert the custom script just before the closing </body> tag
    html_content = html_content.replace('</body>', ajout_script( nt) + '</body>')

    # Write the modified content back to the file
    with open(html_file_path, 'w') as f:
        f.write(html_content)
    


def readGraph_and_write(fileGraph, outputFile):

    with open(fileGraph, "r", encoding="utf-8", errors='ignore') as source_file:
        source_content = source_file.read()

    # Parse le contenu du fichier source avec BeautifulSoup
    source_soup = BeautifulSoup(source_content, "html.parser")

    # Récupère toutes les balises <div> et <script>
    div_tags = source_soup.find_all("div")
    script_tags = source_soup.find_all("script")

    # Ouvre le fichier HTML existant dans lequel on va ajouter les balises
    with open(outputFile, "r", encoding="utf-8") as target_file:
        target_content = target_file.read()

    # Parse le contenu du fichier cible avec BeautifulSoup et récupère la div "TargetDiv"
    target_soup = BeautifulSoup(target_content, "html.parser")
    target_div = target_soup.find("div", class_="TargetDiv")

    if target_div:
        target_div.clear()

        for div in div_tags:
            target_div.append(div)

        for script in script_tags:
            target_div.append(script)

    #Write the html of the graph generated by pyvis in the div with the class "TargetDiv in the file renderer/test.html"
    with open(outputFile, "w", encoding="utf-8") as modified_file:
        modified_file.write(str(target_soup))




def getUserSetting(settingFilePath):
    with open(settingFilePath, 'r', encoding='utf-8') as f:  # Lire avec encodage UTF-8
        data = json.load(f)
    return data



if __name__ == "__main__":

    #Get all the settings of the User in the file in paramater.
    dataUser = getUserSetting("renderer/json/userSettings.json")

    #Il faut 2 argument dans le lancement du script, le premier c'est le sujet et le deuxième "true" si recherche par autheur, "false" sinon.
    if(len(sys.argv) > 2 and len(sys.argv[1]) > 0):
        mot_cle = sys.argv[1]

        if len(sys.argv) >= 2 and sys.argv[2] == "true":  # Vérification du second argument
            liste_final = search_by_author(mot_cle)
            show_graphique_author(liste_final)
        else:
            # Exécution de la recherche par mot clé
            nbNodeOrigin = int(dataUser['ListeNoeudSettings'][0]['value'])
            NbNodeChild = int(dataUser['ListeNoeudSettings'][1]['value'])
            similarities = search_by_keyword(mot_cle,nbNodeOrigin)
            liste_final = [t[0] for t in similarities]
            liste_final = get_list_xSimilaritie(liste_final, NbNodeChild)
            show_graphique(liste_final, dataUser)
        
        #read the file in the first param and write in the second param.
        readGraph_and_write("Bokeh/bin/nx.html", "renderer/test.html")

    else:
        raise ValueError("valeur nul, il doit y avoir une valeur")


#Recherche pas par auteur donc par sujet, recherche sur le sujet carbon
#python3 -m Bokeh.src.mainPyvis "carbon" "false"

#Recherche par auteur.
#python3 -m Bokeh.src.mainPyvis "richard l." "true"