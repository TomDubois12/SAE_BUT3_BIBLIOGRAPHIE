import json
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network
import requests
from BERT.test import search_by_author, search_by_keyword, search_by_keyword_and_compare, find_similar_articles
import sys
from bs4 import BeautifulSoup

def ajout_script(node, network):
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
                doi.textContent = `DOI : ${nodeData.index || "DOI non disponible"}`;
                doi.href = nodeData.doi || "#";  // Set the URL for the link, default to "#" if DOI not available
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
                return None, None, None, None, None, None, None
        else:
            return None, None, None, None, None, None, None
    else:
        return None, None, None, None, None, None, None

    if response.ok:
        data = response.json()
        print("Data retrieved from API:", len(data.get('citations', None)))  # Ajoutez ceci pour déboguer
        title = data.get('title', None)
        abstract = data.get('abstract', None)
        authors = ', '.join([author['name'] for author in data.get('authors', [])])
        doi = data.get('doi', None)
        year = data.get('year', None)
        num_citations = len(data.get('citations', None))
        url_citations = data.get('url', None)

        # Retournez toujours 7 valeurs
        return title, abstract, authors, doi, year, num_citations, url_citations
    else:
        return None, None, None, None, None, None, None

def recuperate_data(data, noms, infos):
    node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
    node_title = dict(zip(noms, data['Title']))
    node_abstract = dict(zip(noms, data['Abstract Note']))
    node_author = dict(zip(noms, data['Author']))
    node_doi = dict(zip(noms, data.index))
    node_year = dict(zip(noms, data['Publication Year']))
    
    # Ajout des dictionnaires pour stocker le nombre de citations et les URLs
    node_num_citations = {}
    node_url_citations = {}
        
    # for nom in noms:
    #     title, abstract, author, doi, year, num_citations, url_citations = semantic_scholar_research(
    #         doi=node_doi[nom] if pd.notna(node_doi[nom]) and node_doi[nom] else None,
    #         title=node_title[nom] if pd.notna(node_title[nom]) and node_title[nom] else None
    #     )
        
    #     # Si les informations de Semantic Scholar sont absentes, gardez celles du CSV
    #     node_title[nom] = title or node_title[nom] or "Titre inconnu"
    #     node_abstract[nom] = abstract or node_abstract[nom] or "Aperçu indisponible"
    #     node_author[nom] = author or node_author[nom] or "Auteur inconnu"
    #     node_doi[nom] = doi or node_doi[nom] or "DOI indisponible"
    #     node_year[nom] = year or node_year[nom] or "Année inconnue"
    #     node_num_citations[nom] = num_citations if num_citations is not None else 0  # Si pas de citations, 0 par défaut
    #     node_url_citations[nom] = url_citations or "URL indisponible"

    return node_info, node_title, node_abstract, node_author, node_doi, node_year, node_num_citations, node_url_citations

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

def show_graphique(liste_key):

    file = 'BERT/Bibliographie_sans_doublon.csv'
    data2 = pd.read_csv(file)
    data = data2.iloc[:, [0,1,2,3,4,5,6,7,8,9,10,11, -1]] #rajout de la colonne nbCitation avec le -1
    # Définir la colonne "Key" comme index
    data.set_index("DOI", inplace=True)

    
    # Supprimer les lignes avec des valeurs NaN dans la colonne "Publication Year"
    # data = data.dropna(subset=["Publication Year"])

    noms = data.index  # Accéder à l'index au lieu de la colonne "Key"
    infos = data.iloc[:, 0:3]  # Prendre les infos (les colonnes restantes)
    annees_data = data["Publication Year"]

    # Rechercher par mot clé
    # mot_cle = "Linear sweep voltammetry at very small stationary disk electrodes"
    # res = search_by_keyword_and_compare(mot_cle)
    # Extraire les clés de la recherchea
    # liste_cles = [(cle, cle2) for cle, cle2, valeur in res if valeur > 0.5]
    # Reindexer le DataFrame selon les clés trouvées
    all_key1 = [t[0] for t in liste_key]
    all_key2 = [t[1] for t in liste_key]
    all_key2 = [t[0] for _t in all_key2 for t in _t]
    dfFinal = data.reindex(all_key1 + all_key2)

    noms = dfFinal.index  # Use the index (the keys)
    infos = dfFinal.iloc[:, 0:3]  # Take the columns that contain the information
    
    node_info, node_title, node_abstract, node_author, node_doi, node_year, node_citations, url_citations = recuperate_data(dfFinal, noms, infos)

    # Create the graph
    G = nx.Graph()

    # Determine the original nodes
    origin_nodes = set(all_key1)  # Take the 15 keys from liste_key

    # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
    for nom in noms:
        color = 'red' if nom in origin_nodes else 'blue'  # Red for origin nodes, blue otherwise
        G.add_node(nom,size=20+500/30 , infos=node_info[nom], year=node_year[nom], title=node_title[nom], abstract=node_abstract[nom], author=node_author[nom], doi=node_doi[nom], color=color, nb_citations=500, citations="blablou")
        
        #G.add_node(nom,size=20+node_citations[nom]/30,label=node_author[nom].split(",")[0] +" "+ str(node_year[nom]) , infos=node_info[nom], year=node_year[nom], title=node_title[nom], abstract=node_abstract[nom], author=node_author[nom], doi=node_doi[nom], color=color, nb_citations=node_citations[nom], citations=url_citations[nom])

    # Add the edges
    for key, keys in liste_key:
        for key2 in keys:
            G.add_edge(key, key2[0],length=(500 - ((key2[1] - 0.7) / (1 - 0.7)) * (500 - 20)), color="000000")
    
        # Visualiser avec PyVis
    nt = Network('100vh', '100vw', notebook=True)
    # nt.show_buttons(filter_=['physics'])
    nt.from_nx(G)

    # Set the color of the nodes in Pyvis
    for node in G.nodes(data=True):
        nt.get_node(node[0])['color'] = node[1]['color']
        
    nt.show('Bokeh/bin/nx.html')

    # Create the HTML file
    html_file_path = 'Bokeh/bin/nx.html'
    nt.save_graph(html_file_path)

    # Manually modify the HTML to include the JavaScript functionality
    with open(html_file_path, 'r') as f:
        html_content = f.read()
    
    # Insert the custom script just before the closing </body> tag
    html_content = html_content.replace('</body>', ajout_script(node, nt) + '</body>')

    # Write the modified content back to the file
    with open(html_file_path, 'w') as f:
        f.write(html_content)

def show_graphique_author(liste_key, mot_cle):
    file = 'BERT/Bibliographie_sans_doublon.csv'
    data2 = pd.read_csv(file)
    data = data2.iloc[:, [0,1,2,3,4,5,6,7,8,9,10,11, -1]] #rajout de la colonne nbCitation avec le -1


    # Définir la colonne "Key" comme index
    data.set_index("DOI", inplace=True)

    # Supprimer les lignes avec des valeurs NaN dans la colonne "Publication Year"
    # data = data.dropna(subset=["Publication Year"])

    noms = data.index  # Accéder à l'index au lieu de la colonne "Key"
    infos = data.iloc[:, 0:3]  # Prendre les infos (les colonnes restantes)
    annees_data = data["Publication Year"]

    # Rechercher par mot clé
    # mot_cle = "Linear sweep voltammetry at very small stationary disk electrodes"
    # res = search_by_keyword_and_compare(mot_cle)
    # Extraire les clés de la recherche
    # liste_cles = [(cle, cle2) for cle, cle2, valeur in res if valeur > 0.5]
    # Reindexer le DataFrame selon les clés trouvées
    all_key1 = liste_key


    dfFinal = data.reindex(all_key1)

    noms = dfFinal.index  # Utiliser l'index (les clés)
    infos = dfFinal.iloc[:, 0:3]  # Prendre les colonnes qui contiennent les informations
    
    node_info, node_title, node_abstract, node_author, node_doi, node_year, node_citations, url_citations = recuperate_data(dfFinal, noms, infos)

    # Create the graph
    G = nx.Graph()

    # Determine the original nodes
    origin_nodes = set(all_key1)  # Take the 15 keys from liste_key

    # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
    for nom in noms:
        color = 'red' if nom in origin_nodes else 'blue'  # Red for origin nodes, blue otherwise
        G.add_node(nom,size= 20+node_citations[nom]/30, infos=node_info[nom], year=node_year[nom], title=node_title[nom], abstract=node_abstract[nom], author=node_author[nom], doi=node_doi[nom], color=color, nb_citations=node_citations[nom], citations=url_citations[nom])

    # Déterminer les 15 nœuds d'origine

    list_tuple_cles = []
    for i in range(len(liste_key)):
        for j in range(i,len(liste_key)):
            list_tuple_cles.append((liste_key[i],liste_key[j]))
    
    liste_cle1_cle2 = []    
    for key in liste_key:
        articles_similaire = find_similar_articles(key, 3)
        for elem in articles_similaire:
           
            if elem[0] in liste_key:
                liste_cle1_cle2.append((key,elem[0]))
                G.add_edge(key,elem[0],color="000000", length=(500 - ((elem[1] - 0.7) / (1 - 0.7)) * (500 - 20))) # calcule pour que la talle mini de l'edge soit20 et max 500 et qu'il prenne en compte que à partir d'une similarité > a 0.7 sinon 500
    #G.add_edges_from(liste_cle1_cle2, color="000000")


         # Visualiser avec PyVis
    nt = Network('100vh', '100vw', notebook=True)
    # nt.show_buttons(filter_=['physics'])
    nt.from_nx(G)

    # Set the color of the nodes in Pyvis
    for node in G.nodes(data=True):
        nt.get_node(node[0])['color'] = node[1]['color']
        
    nt.show('Bokeh/bin/nx.html')

    # Create the HTML file
    html_file_path = 'Bokeh/bin/nx.html'
    nt.save_graph(html_file_path)

    # Manually modify the HTML to include the JavaScript functionality
    with open(html_file_path, 'r') as f:
        html_content = f.read()
    
    # Insert the custom script just before the closing </body> tag
    html_content = html_content.replace('</body>', ajout_script(node, nt) + '</body>')

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



if __name__ == "__main__":
    if(len(sys.argv) > 2 and len(sys.argv[1]) > 0):
        mot_cle = sys.argv[1]

        if len(sys.argv) >= 2 and sys.argv[2] == "true":  # Vérification du second argument
            liste_final = search_by_author(mot_cle)
            show_graphique_author(liste_final,mot_cle)
        else:
            # Exécution de la recherche par mot clé
            similarities = search_by_keyword(mot_cle)
            liste_final = [t[0] for t in similarities]
            liste_final = get_list_xSimilaritie(liste_final, 5)
            show_graphique(liste_final)
        
        readGraph_and_write("Bokeh/bin/nx.html", "renderer/test.html")

    else:
        raise ValueError("valeur nul, il doit y avoir une valeur")

    


    






#python3 -m Bokeh.src.mainPyvis "carbon" "false"
#Recherche pas par auteur donc par sujet, recherche sur le sujet carbon

#python3 -m Bokeh.src.mainPyvis "richard l." "true"
#Recherche par auteur.