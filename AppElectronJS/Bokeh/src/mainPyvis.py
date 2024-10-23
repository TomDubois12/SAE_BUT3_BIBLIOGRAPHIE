import json
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network
from BERT.test import search_by_author, find_similar_articles, search_by_keyword, search_by_keyword_and_compare
import sys
    

def get_list_xSimilaritie(listeKey, x=5):
    """
    Take a liste of key, for exemple 15 key similar from the keyWords and return a list of x similar article for each key.
    return a list of list with 2 element, first: the key. second: a list of key of x article similar 
    """
    liste_final = []
    for key in listeKey:
        listeSimiliarities = find_similar_articles(key, x)
        liste_final += [[key, [t[0] for t in listeSimiliarities]]]
    return liste_final

def show_graphique(liste_key):
    file = 'Bokeh/data/Bibliographie.csv'
    data2 = pd.read_csv(file)
    data = data2.iloc[:, :12]

    # Définir la colonne "Key" comme index
    data.set_index("Key", inplace=True)

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
    all_key2 = [t[i] for t in all_key2 for i in range(len(t))]

    dfFinal = data.reindex(all_key1 + all_key2)

    noms = dfFinal.index  # Utiliser l'index (les clés)
    infos = dfFinal.iloc[:, 0:3]  # Prendre les colonnes qui contiennent les informations

    # Créer un dictionnaire d'informations pour les nœuds
    node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
    node_year = dict(zip(noms, annees_data.reindex(noms)))  # Reindexer les années pour qu'elles correspondent aux clés/noms

    # Créer le graphe
    G = nx.Graph()

    # Déterminer les 15 nœuds d'origine
    origin_nodes = set(all_key1)  # Prendre les 15 clés de liste_key

    # Ajouter les nœuds avec les attributs 'infos' et 'year', en définissant la couleur
    for nom in noms:
        color = 'red' if nom in origin_nodes else 'blue'  # Rouge pour les nœuds d'origine, bleu sinon
        G.add_node(nom, infos=node_info[nom], year=node_year[nom], color=color)

    # Grouper par année et ajouter les arêtes
    # print(grouped_by_annee)
    for key, keys in liste_key:
        list_tuple_cles = [(key, t) for t in keys]
        G.add_edges_from(list_tuple_cles, color="000000")

    # for group in grouped_by_annee:
    #    G.add_edges_from((group[i], group[j]) for i in range(len(group)) for j in range(i + 1, len(group)))

    # Visualiser avec PyVis
    nt = Network('100vh', '100vw', notebook=True)
    nt.show_buttons(filter_=['physics'])
    nt.from_nx(G)

    # Définir la couleur des nœuds dans Pyvis
    for node in G.nodes(data=True):
        nt.get_node(node[0])['color'] = node[1]['color']

    nt.show('Bokeh/bin/nx.html')



def show_graphique_author(liste_key, mot_cle):
    file = 'Bokeh/data/Bibliographie.csv'
    data2 = pd.read_csv(file)
    data = data2.iloc[:, :12]

    # Définir la colonne "Key" comme index
    data.set_index("Key", inplace=True)

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

    # Créer un dictionnaire d'informations pour les nœuds
    node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
    node_year = dict(zip(noms, annees_data.reindex(noms)))  # Reindexer les années pour qu'elles correspondent aux clés/noms

    # Créer le graphe
    G = nx.Graph()

    # Déterminer les 15 nœuds d'origine

    # Ajouter les nœuds avec les attributs 'infos' et 'year', en définissant la couleur
    for nom in noms:
        color = 'red' # Rouge pour les nœuds d'origine, bleu sinon
        G.add_node(nom, infos=node_info[nom], year=node_year[nom], color=color)


    list_tuple_cles = []
    for i in range(len(liste_key)):
        for j in range(i,len(liste_key)):
            list_tuple_cles.append((liste_key[i],liste_key[j]))
    

    liste_cle1_cle2 = []
    for key in liste_key:
        articles_similaire = find_similar_articles(key, 3)
        for elem in articles_similaire:
            print(elem, key)
            if elem[0] in liste_key:
                liste_cle1_cle2.append((key,elem[0]))
    G.add_edges_from(liste_cle1_cle2, color="000000")
    # for key in liste_key:
    #     list_tuple_cles = [(key, t) for t in keys]
    #     G.add_edges_from(list_tuple_cles, color="000000")

    # for group in grouped_by_annee:
    #    G.add_edges_from((group[i], group[j]) for i in range(len(group)) for j in range(i + 1, len(group)))

    # Visualiser avec PyVis
    nt = Network('100vh', '100vw', notebook=True)
    nt.show_buttons(filter_=['physics'])
    nt.from_nx(G)

    # Définir la couleur des nœuds dans Pyvis
    for node in G.nodes(data=True):
        nt.get_node(node[0])['color'] = node[1]['color']
        
    nt.show('Bokeh/bin/nx.html')


if __name__ == "__main__":
    print("-" * 50)
    
    query = sys.argv[1]
    mot_cle = query
    if len(sys.argv) >= 2 and sys.argv[2] == "True":  # Vérification du second argument
        liste_final = search_by_author(mot_cle)
        show_graphique_author(liste_final,mot_cle)
    else:
        # Exécution de la recherche par mot clé
        
        similarities = search_by_keyword(mot_cle)
        liste_final = [t[0] for t in similarities]
        liste_final = get_list_xSimilaritie(liste_final, 5)
        show_graphique(liste_final)

