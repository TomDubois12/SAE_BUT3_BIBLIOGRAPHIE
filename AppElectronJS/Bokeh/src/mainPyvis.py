import json
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network
from BERT.test import search_by_author, find_similar_articles, search_by_keyword, search_by_keyword_and_compare
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
            
                const abstract = document.createElement("p");
                abstract.classList.add("pAbstract");
                abstract.textContent = `Abstract : ${nodeData.abstract || "Abstract non disponible"}`;
                aside.appendChild(abstract);
                
                const doi = document.createElement("a");
                doi.classList.add("pDOI");
                doi.textContent = `DOI : ${nodeData.doi || "DOI non disponible"}`;
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

def recuperate_data(data, noms, infos):
    
    # Create a dictionary of information for the nodes, including the title
    node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
    #node_year = dict(zip(noms, annees_data.reindex(noms)))  # Reindex years to match the keys/names

    # Add title as a node attribute for each publication
    node_title = dict(zip(noms, data['Title']))
    node_abstract = dict(zip(noms, data['Abstract Note']))
    node_author = dict(zip(noms, data['Author']))
    node_doi = dict(zip(noms, data['Url']))
    node_year = dict(zip(noms, data['Publication Year']))
    return node_info, node_title, node_abstract, node_author, node_doi, node_year

    

def get_list_xSimilaritie(listeKey, x=5):
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
    data = data2.iloc[:, :12]

    # Définir la colonne "Key" comme index
    data.set_index("DOI", inplace=True)
    print(liste_key)

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
    all_key1 = [t[0] for t in liste_key]
    all_key2 = [t[1] for t in liste_key]
    all_key2 = [t[0] for _t in all_key2 for t in _t]
    dfFinal = data.reindex(all_key1 + all_key2)

    noms = dfFinal.index  # Use the index (the keys)
    infos = dfFinal.iloc[:, 0:3]  # Take the columns that contain the information
    
    node_info, node_title, node_abstract, node_author, node_doi, node_year = recuperate_data(dfFinal, noms, infos)

    # Create the graph
    G = nx.Graph()

    # Determine the original nodes
    origin_nodes = set(all_key1)  # Take the 15 keys from liste_key

    # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
    for nom in noms:
        color = 'red' if nom in origin_nodes else 'blue'  # Red for origin nodes, blue otherwise
        G.add_node(nom, infos=node_info[nom], year=node_year[nom], title=node_title[nom], abstract=node_abstract[nom], author=node_author[nom], doi=node_doi[nom], color=color)

    # Add the edges
    for key, keys in liste_key:
        for key2 in keys:
            print(key, key2)
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
    data = data2.iloc[:, :12]

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
    
    node_info, node_title, node_abstract, node_author, node_doi, node_year = recuperate_data(dfFinal, noms, infos)

    # Create the graph
    G = nx.Graph()

    # Determine the original nodes
    origin_nodes = set(all_key1)  # Take the 15 keys from liste_key

    # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
    for nom in noms:
        color = 'red' if nom in origin_nodes else 'blue'  # Red for origin nodes, blue otherwise
        G.add_node(nom, infos=node_info[nom], year=node_year[nom], title=node_title[nom], abstract=node_abstract[nom], author=node_author[nom], doi=node_doi[nom], color=color)

    # Déterminer les 15 nœuds d'origine

    list_tuple_cles = []
    for i in range(len(liste_key)):
        for j in range(i,len(liste_key)):
            list_tuple_cles.append((liste_key[i],liste_key[j]))
    
    print("****"*100)
    liste_cle1_cle2 = []    
    for key in liste_key:
        articles_similaire = find_similar_articles(key, 3)
        for elem in articles_similaire:
           
            if elem[0] in liste_key:
                print(elem, key)
                liste_cle1_cle2.append((key,elem[0]))
                G.add_edge(key,elem[0], length=(500 - ((elem[1] - 0.7) / (1 - 0.7)) * (500 - 20))) # calcule pour que la talle mini de l'edge soit20 et max 500 et qu'il prenne en compte que à partir d'une similarité > a 0.7 sinon 500
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

if __name__ == "__main__":
    print("-" * 50)
    
    query = sys.argv[1]
    mot_cle = query
    if len(sys.argv) >= 2 and sys.argv[2] == "true":  # Vérification du second argument
        print("lalalalalallalalalallalallalalalal"*10)
        liste_final = search_by_author(mot_cle)
        print(liste_final)
        show_graphique_author(liste_final,mot_cle)
    else:
        # Exécution de la recherche par mot clé
        print("lalalalalallalalalallalallalalalal")
        similarities = search_by_keyword(mot_cle)
        liste_final = [t[0] for t in similarities]
        liste_final = get_list_xSimilaritie(liste_final, 5)
        show_graphique(liste_final)


    with open("Bokeh/bin/nx.html", "r", encoding="utf-8", errors='ignore') as source_file:
        print(source_file)
        source_content = source_file.read()

    # Parse le contenu du fichier source avec BeautifulSoup
    source_soup = BeautifulSoup(source_content, "html.parser")

    # Récupère toutes les balises <div> et <script>
    div_tags = source_soup.find_all("div")
    script_tags = source_soup.find_all("script")

    # Ouvre le fichier HTML existant dans lequel on va ajouter les balises
    with open("renderer/test.html", "r", encoding="utf-8") as target_file:
        target_content = target_file.read()

    # Parse le contenu du fichier cible avec BeautifulSoup
    target_soup = BeautifulSoup(target_content, "html.parser")
    target_div = target_soup.find("div", class_="TargetDiv")
    # Trouve le <body> dans le fichier cible

    if target_div:
        # Vide le contenu existant de la balise <div>
        target_div.clear()

        # Ajoute les nouvelles balises <div> à l'intérieur
        for div in div_tags:
            target_div.append(div)

        for script in script_tags:
            target_div.append(script)

        print("Le contenu de la balise <div> avec la classe 'saluttoi' a été remplacé.")

    # Écrit les changements dans le fichier cible
    with open("renderer/test.html", "w", encoding="utf-8") as modified_file:
        modified_file.write(str(target_soup))

    print("Les balises <div> et <script> ont été ajoutées à 'fichier_cible.html'")
#python3 -m Bokeh.src.mainPyvis "carbon" "false"
#Recherche pas par auteur donc par sujet, recherche sur le sujet carbon

#python3 -m Bokeh.src.mainPyvis "richard l." "true"
#Recherche par auteur.
