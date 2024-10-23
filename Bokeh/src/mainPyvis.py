import json
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network
from BERT.test import find_similar_articles, search_by_keyword

def get_list_xSimilaritie(listeKey, x=5):
    """
    Take a list of key, for example 15 key similar from the keyWords and return a list of x similar articles for each key.
    return a list of lists with 2 elements: first - the key, second - a list of keys of x similar articles.
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

    # Define the "Key" column as the index
    data.set_index("Key", inplace=True)

    noms = data.index  # Access the index instead of the "Key" column
    infos = data.iloc[:, 0:3]  # Take the info (the remaining columns)
    annees_data = data["Publication Year"]

    all_key1 = [t[0] for t in liste_key]
    all_key2 = [t[1] for t in liste_key]
    all_key2 = [t[i] for t in all_key2 for i in range(len(t))]

    dfFinal = data.reindex(all_key1 + all_key2)

    noms = dfFinal.index  # Use the index (the keys)
    infos = dfFinal.iloc[:, 0:3]  # Take the columns that contain the information

    # Create a dictionary of information for the nodes
    node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
    node_year = dict(zip(noms, annees_data.reindex(noms)))  # Reindex years to match the keys/names

    # Create the graph
    G = nx.Graph()

    # Determine the original nodes
    origin_nodes = set(all_key1)  # Take the 15 keys from liste_key

    # Add the nodes with attributes 'infos' and 'year', defining the color
    for nom in noms:
        color = 'red' if nom in origin_nodes else 'blue'  # Red for origin nodes, blue otherwise
        G.add_node(nom, infos=node_info[nom], year=node_year[nom], color=color)

    # Add the edges
    for key, keys in liste_key:
        list_tuple_cles = [(key, t) for t in keys]
        G.add_edges_from(list_tuple_cles, color="000000")

    # Visualize with PyVis
    nt = Network('100vh', '100vw', notebook=True)
    nt.show_buttons(filter_=['physics'])
    nt.from_nx(G)

    # Set the color of the nodes in Pyvis
    for node in G.nodes(data=True):
        nt.get_node(node[0])['color'] = node[1]['color']

    # Create the HTML file
    html_file_path = 'Bokeh/bin/nx.html'
    nt.save_graph(html_file_path)

    # Manually modify the HTML to include the JavaScript functionality
    with open(html_file_path, 'r') as f:
        html_content = f.read()

    # Add custom script for handling node clicks
    custom_script = """
    <script type="text/javascript" src="Bokeh/bin/lib/binding/utils.js"></script>
    <script type="text/javascript">
        function onNodeClick(params) {
            if (params.nodes.length > 0) {
                console.log("Clicked node:", params.nodes[0]);
                // Here you can add more functionality, like fetching data
            }
        }
        network.on("click", onNodeClick);
    </script>
    """
    
    # Insert the custom script just before the closing </body> tag
    html_content = html_content.replace('</body>', custom_script + '</body>')

    # Write the modified content back to the file
    with open(html_file_path, 'w') as f:
        f.write(html_content)

print("-" * 50)
mot_cle = "Linear sweep voltammetry at very small stationary disk electrodes"
similarities = search_by_keyword(mot_cle)

liste_final = [t[0] for t in similarities]
liste_final = get_list_xSimilaritie(liste_final, 5)

show_graphique(liste_final)
