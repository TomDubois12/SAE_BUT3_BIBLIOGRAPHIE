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
    <script type="text/javascript">
        function onNodeInteraction(params) {
            const canva = document.getElementsByClassName('contenerCanvaAside')[0]; // Accès au premier élément
            const className = 'generated-div';
            const nodeId = params.nodes[0];
            
            // Retrieve the title from the node attributes
            const nodeData = network.body.data.nodes.get(nodeId); // Utiliser un autre nom pour éviter la confusion
            console.log(nodeData);
            // Check for existing aside element by ID
            const existingIdenticalElement = document.getElementById(nodeId);
            
            // If the existing aside is found, remove it
            if (existingIdenticalElement) {
                existingIdenticalElement.remove();
            } else {
                const existingElements = document.getElementsByClassName(className);
                // Remove the first existing element if it exists
                if (existingElements.length > 0) {
                    existingElements[0].remove();
                }
                
                if (!nodeId) {
                    existingElements[0].remove();
                }

                // Create a new aside element
                const aside = document.createElement("aside");

                // Add content to the aside, including the title
                const titre = document.createElement("h1");
                titre.classList.add("pTitle");
                titre.textContent = `Titre de la publication : ${nodeData.title || "Titre non disponible"}`;
                aside.appendChild(titre);
                
                const author = document.createElement("p");
                author.classList.add("pAuthor");
                author.textContent = `Auteur(s), co-auteur(s) : ${nodeData.author || "Auteur(s) non disponible"}`;
                aside.appendChild(author);
            
                const year = document.createElement("p");
                year.classList.add("pYear");
                year.textContent = `Année de publication : ${nodeData.year || "Année non disponible"}`;
                aside.appendChild(year);
                
                const nb_citation = document.createElement("p");
                nb_citation.classList.add("pCitation");
                nb_citation.textContent = `Nombre de citations : ${nodeData.nb_citations || "Nombre de citation non disponible"}`;
                aside.appendChild(nb_citation);
            
                const abstract = document.createElement("p");
                abstract.classList.add("pAbstract");
                abstract.textContent = `Abstract : ${nodeData.abstract || "Abstract non disponible"}`;
                aside.appendChild(abstract);
                
                const doi = document.createElement("a");
                doi.classList.add("pDOI");
                doi.textContent = `DOI : ${nodeData.url || "DOI non disponible"}`;
                doi.href = nodeData.url || "#";  // Set the URL for the link, default to "#" if DOI not available

                doi.target = "_blank";  // Open the link in a new tab
                doi.rel = "noopener noreferrer";  // Security measure to prevent exploitation
                aside.appendChild(doi);
     
                aside.classList.add(className); // Add class for styling
                aside.id = nodeId; // Assign unique ID

                // Append the aside to the DOM
                canva.appendChild(aside);
                console.log(`Un nouvel aside a été créé pour ${nodeId} avec le titre "${nodeData.title || "Titre non disponible"}" publié en "${nodeData.year || "Année non disponible"}".`);
            }

            if (params.nodes.length > 0) {
                console.log("Clicked node:", nodeId);
                // Here you can add more functionality, like fetching data
            }
        }
        
        network.on("click", onNodeInteraction);
        network.on("hoverNode", onNodeInteraction);
    </script>      
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
        print("Data retrieved from API:", len(data.get('citations', None)))
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
    # Vérifier si le fichier cache existe, sinon le créer avec un dictionnaire vide
    if not os.path.exists(cache_file):
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    # Charger le cache existant
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)

    if doi:
        # Ajouter ou mettre à jour les informations de DOI dans le cache
        cache_data[doi] = {
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'year': year,
            'num_citations': num_citations,
            'doi_citations': doi_citations,
            'url': url
        }
    
        # Sauvegarder les données mises à jour dans le fichier cache
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=4)


def recuperate_data(data, noms, infos):
    #node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
    node_title = dict(zip(noms, data['Title']))
    #node_abstract = dict(zip(noms, data['Abstract Note']))
    #node_author = dict(zip(noms, data['Author']))
    node_doi = dict(zip(noms, data.index))
    #node_year = dict(zip(noms, data['Publication Year']))
    
    cache_file = 'cache_doi.json'
    
    # Initialisation des dictionnaires pour stocker le nombre de citations et les URLs
    num_citations = 0
    doi_citations = {}
    url = ""
    
    # Charger le cache si disponible, sinon initialiser un cache vide
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
    else:
        cache_data = {}  # Si le fichier n'existe pas, initialiser un cache vide

    for nom in noms:
        # Vérifier si le DOI est dans le cache
        doi = node_doi[nom]
        if doi in cache_data:
            num_citations = cache_data[doi]['num_citations']
            doi_citations = cache_data[doi]['doi_citations']
        else:
            # Appel à Semantic Scholar si les données ne sont pas en cache
            title, abstract, author, doi, year, num_citations, doi_citations, url = semantic_scholar_research(
                doi=node_doi[nom] if pd.notna(node_doi[nom]) and node_doi[nom] else None,
                title=node_title[nom] if pd.notna(node_title[nom]) and node_title[nom] else None
            )
        
            # Si les informations de Semantic Scholar sont absentes, garder celles du CSV
            titre = title or "Titre inconnu"
            resume = abstract or "Aperçu indisponible"
            author = author or "Auteur inconnu"
            node_doi[nom] = doi or "DOI indisponible"
            pub_year = year or "Année inconnue"
            num_citations = num_citations if num_citations is not None else 0  # Si pas de citations, 0 par défaut
            doi_citations = doi_citations or "Pas de citations"
            node_url = url or "URL indisponible"
            
            # Mettre à jour le cache avec les nouvelles données
            cache(doi, title, abstract, author, year, url, num_citations, doi_citations)
    
    return titre, resume, author, node_doi, pub_year, num_citations, doi_citations, node_url



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
            ...
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


def find_min_max_values(dico):
    #return the min and max of a dico like this {"DOI": nbCitation}
    min_key = min(dico, key=dico.get)
    max_key = max(dico, key=dico.get)
    return dico[min_key], dico[max_key]


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
        node_title, node_abstract, node_author, node_doi, node_year, node_citations, url_citations, node_url = recuperate_data(dfFinal, noms, infos)

        # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        minTaille, maxTaille = find_min_max_values(node_citations)
        
            # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
    for nom in noms:
        nodeTaille = transform_value_log(node_citations[nom], minTaille, maxTaille)
        color = 'red' if nom in originKeys else 'blue'  # Red for origin nodes, blue otherwise
        
        G.add_node(
            nom,
            size=nodeTaille,
            label=node_author.split(",")[0] +" "+ str(node_year),
            year=node_year,
            title=node_title,
            abstract=node_abstract,
            author=node_author,
            doi=node_doi,
            color=color,
            nb_citations=node_citations,
            citations=doi_citations,
            url=node_url,
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
    
    node_title, node_abstract, node_author, node_doi, node_year, node_citations, doi_citations, node_url = recuperate_data(dfFinal, noms, infos)
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
        node_title, node_abstract, node_author, node_doi, node_year, node_citations, url_citations, node_url = recuperate_data(dfFinal, noms, infos)

        # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        minTaille, maxTaille = find_min_max_values(node_citations)
    
        for nom in noms:
        nodeTaille = transform_value_log(node_citations[nom], minTaille, maxTaille)
        color = 'red' if nom in originKeys else 'blue'  # Red for origin nodes, blue otherwise
        
        G.add_node(
            nom,
            size=nodeTaille,
            label=node_author.split(",")[0] +" "+ str(node_year),
            year=node_year,
            title=node_title,
            abstract=node_abstract,
            author=node_author,
            doi=node_doi,
            color=color,
            nb_citations=node_citations,
            citations=doi_citations,
            url=node_url,
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