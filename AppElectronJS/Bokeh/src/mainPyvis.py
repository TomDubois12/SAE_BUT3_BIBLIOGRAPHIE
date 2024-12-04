import json
import pandas as pd
import networkx as nx
from pyvis.network import Network
from BERT.search_utils import search_by_author, search_by_keyword, find_similar_articles, search_by_title
import sys
from bs4 import BeautifulSoup
import os
import math
from pandas import json_normalize

cache_file = 'cache_doi.json'
if os.path.exists(cache_file):
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
else:
    cache_data = {}  # If the cache doesn't exist, initialize an empty dictionary

def ajout_script():
    # Add custom script for handling node clicks and displaying the publication title
    custom_script = """
    <div id="result"></div>
    <script type="text/javascript" src="Bokeh/bin/lib/binding/utils.js"></script>
    <script src="js/EventNodeEdge.js"> </script>
    """
    return custom_script


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


def setLiaison(G, liaison, allTheKeys, listeKeys):
    match liaison['liaisonName']:
        case 'Similarité':
            # Add the edges based on similarity
            for key, keys in listeKeys:
                for key2 in keys:
                    G.add_edge(key, key2[0], length=(500 - ((key2[1] - 0.7) / (1 - 0.7)) * (500 - 20)), color=liaison['color'])
        
        # case 'Citation':
        #     allTheKeys = set(allTheKeys)
        #     set_liaison_final = set()

        #     for key in allTheKeys:
        #         normalized_key = key.lower()

        #         if normalized_key in cache_data:
        #             liste_doi = cache_data[normalized_key].get("doi_citations", [])
        #             for keyCite in liste_doi:
        #                 if key in cache_data.keys() and keyCite in cache_data.keys() and keyCite in allTheKeys:
        #                     set_liaison_final.add((key, keyCite))  # Add citation relationship

        #     # Add the edges with arrows (for citation)
        #     for couple in set_liaison_final:
        #         G.add_edge(couple[0], couple[1], color=liaison['color'], arrows='to')
                
        # case 'Référence':
        #     allGraphNode = set(allTheKeys)
            
        #     for node in allGraphNode:
        #         print(f"{node}, nom : {cache_data[node].get("title")}\n")
        #         normalized_key = node.lower()
                
        #         liste_references_du_node = cache_data[normalized_key].get("doi_references", [])
        #         print(f"a comme source : {cache_data[node].get("doi_references",[])}\n")
        #         for reference in liste_references_du_node:
        #             if(reference != "DOI indisponible"):
        #                 print(reference)
        #                 if reference in allGraphNode:  
        #                     print(f"LIEN DANS LE GRAPHE {reference}, nom : {cache_data[reference.lower()].get("title")}\n")
        #                     if cache_data[node] == "10.1016/0008-6223(94)90158-9" and cache_data[reference] == "10.1063/1.330025":
        #                         G.add_edge(node, reference, color='blue', arrows='from')
        #                     else:    
        #                         G.add_edge(node, reference, color='red', arrows='to')

        case 'Référence':
            allGraphNode = set(allTheKeys)

            for node in allGraphNode:
                liste_references_du_node = cache_data[node].get("doi_references", [])
                for node_second in allGraphNode:
                    if node_second != node and node_second in liste_references_du_node:
                        G.add_edge(node, node_second, color="red", arrows='to')


        case 'Date de publication':
            # Group the articles by their publication year
            year_dict = {}
            for doi, data in cache_data.items():
                publication_year = data.get('year')
                if publication_year:  # Ensure there's a year available
                    if publication_year not in year_dict:
                        year_dict[publication_year] = []
                    year_dict[publication_year].append(doi)
            
            # Add edges between articles published in the same year
            for year, doais in year_dict.items():
                for i in range(len(doais) - 1):
                    if doais[i] in allTheKeys:
                        for j in range(i + 1, len(doais)):
                            G.add_edge(doais[i], doais[j], color=liaison['color'])

    return G



def find_min_max_values(dico):
    liste = set()
    for nom in dico.keys():
        liste.add(dico[nom]['num_citations'])
        print(liste)

    #return the min and max of a dico like this {"DOI": nbCitation}
    min_key = min(liste)
    max_key = max(liste)
    return min_key, max_key


def transform_value_log(value, original_min, original_max, target_min=20, target_max=100):    
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
    
    def setAllNode(G):

        # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        minTaille, maxTaille = find_min_max_values(cache_data)
        
            # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        for nom in noms:
            node = cache_data[nom]
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
                #citations=node['doi_citations'],
                url=node['url'],
                isOrigin=nom in originKeys
            )
        return G


    # Create the graph
    G = nx.Graph()
    

    df = json_normalize(cache_data)

    # Reindexer le DataFrame selon les clés trouvées
    allTheKeys, originKeys, _childKeys = getListallKey(liste_key)
    dfFinal = df.reindex(allTheKeys)

    noms = dfFinal.index  # Use the index (the keys)
    infos = dfFinal.iloc[:, 0:3]  # Take the columns that contain the information
    
    originKeys = set(originKeys)#Transform the list in a set for faster reserch in the list

    G = setAllNode(G)


    liaisons = dataUser["ColorPickerSettings"]

    for liaison in liaisons:
        if liaison['check'] == 'true':
            G = setLiaison(G, liaison, allTheKeys, liste_key)

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
    html_content = html_content.replace('</body>', ajout_script() + '</body>')

    # Write the modified content back to the file
    with open(html_file_path, 'w') as f:
        f.write(html_content)



def show_graphique_author(liste_key):

    def setAllNode(G):       

        # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        minTaille, maxTaille = find_min_max_values(cache_data)
        
            # Add the nodes with attributes 'infos', 'title', and 'year', defining the color
        for nom in noms:
            node = cache_data[nom]
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
                #citations=node['doi_citations'],
                url=node['url'],
                isOrigin="true"
            )
        return G

    # Create the graph
    G = nx.Graph()
    
    df = json_normalize(cache_data)

    # Reindexer le DataFrame selon les clés trouvées
    dfFinal = df.reindex(liste_key)

    noms = dfFinal.index  # Use the index (the keys)
    
    originKeys = set(liste_key)#Transform the list in a set for faster reserch in the list

    G = setAllNode(G)

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
            G = setLiaison(G, liaison, liste_key, liste_cle1_cle2)


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
    html_content = html_content.replace('</body>', ajout_script() + '</body>')

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

        if len(sys.argv) >= 2:
            match sys.argv[2]:
                case "sujet":
                    # Exécution de la recherche par mot clé
                    nbNodeOrigin = int(dataUser['ListeNoeudSettings'][0]['value'])
                    NbNodeChild = int(dataUser['ListeNoeudSettings'][1]['value'])
                    similarities = search_by_keyword(mot_cle,nbNodeOrigin)
                    liste_final = [t[0] for t in similarities]
                    liste_final = get_list_xSimilaritie(liste_final, NbNodeChild)
                    show_graphique(liste_final, dataUser)
                case "auteur":
                    liste_final = search_by_author(mot_cle)
                    show_graphique_author(liste_final)
                case "titre":
                    liste_final = search_by_title(mot_cle)
                    show_graphique_author(liste_final)
        readGraph_and_write("Bokeh/bin/nx.html", "renderer/test.html")

    else:
        raise ValueError("valeur nul, il doit y avoir une valeur")


#Recherche pas par auteur donc par sujet, recherche sur le sujet carbon
#python3 -m Bokeh.src.mainPyvis "carbon" "sujet"

#Recherche par auteur.
#python3 -m Bokeh.src.mainPyvis "richard l." "auteur"