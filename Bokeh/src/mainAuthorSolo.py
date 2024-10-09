import pandas as pd
import networkx as nx
from bokeh.plotting import figure, show, from_networkx, output_file, save
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxZoomTool, PanTool, ResetTool, WheelZoomTool
from bokeh.models.graphs import NodesAndLinkedEdges
from bokeh.palettes import Spectral4, Category10
from bokeh.embed import components
import json
import numpy as np
import time

# Charger les données
file = '../data/test100.csv'
data2 = pd.read_csv(file)
data = data2.iloc[:, :12]
output_file(filename="../bin/mainAuthorSolo.html", title="NodeByAuthor")

# Supprimer les lignes avec des valeurs NaN dans la colonne "Author"
data = data.dropna(subset=["Author"])

# Créer un graphe
G = nx.Graph()

# Pré-calculer les informations pour chaque nœud
start = time.time()

# Créer des nœuds pour chaque ligne
node_info = {}  # Dictionnaire pour stocker les informations des nœuds
for index, row in data.iterrows():
    node_name = f"Node {index}"  # Nommez chaque nœud par son index ou utilisez une autre méthode de nommage
    info = dict(row[1:4])  # Prendre les informations pertinentes pour ce nœud
    node_info[node_name] = json.dumps(info, ensure_ascii=False)  # Ajouter les infos en JSON
    G.add_node(node_name, infos=node_info[node_name], year=row["Publication Year"])  # Ajouter le nœud

end = time.time()
print(f"Temps d'exécution de la partie nœuds: {end - start:.5f} secondes")

# Relier les nœuds par auteur
start = time.time()

# Créer un dictionnaire pour garder trace des auteurs et des nœuds qui leur sont associés
author_nodes = {}

# Pour chaque ligne, trouver les auteurs et relier les nœuds
for index, row in data.iterrows():
    authors = row["Author"].split(";")  # Séparer les auteurs
    authors = [author.strip() for author in authors]  # Enlever les espaces superflus
    node_name = f"Node {index}"  # Nom du nœud associé à la ligne

    for author in authors:
        if author not in author_nodes:
            author_nodes[author] = []  # Initialiser une liste pour les nœuds associés
        author_nodes[author].append(node_name)  # Ajouter le nœud à la liste des nœuds associés à cet auteur

# Ajouter des arêtes entre les nœuds qui partagent le même auteur
for nodes in author_nodes.values():
    print(nodes)
    if len(nodes) > 1:  # Assurez-vous qu'il y a au moins deux nœuds pour créer une arête
        G.add_edges_from((nodes[i], nodes[j]) for i in range(len(nodes)) for j in range(i + 1, len(nodes)))

end = time.time()
print(f"Temps d'exécution de la partie arêtes: {end - start:.5f} secondes")

# Définir une grille de positions pour répartir les groupes dans tout l'espace
n_groups = len(node_info)
grid_size = int(np.ceil(np.sqrt(n_groups)))  # Taille de la grille pour les centres
padding = 4  # Distance entre les groupes

# Stocker les positions des nœuds
positions = {}
group_colors = {}  # Stocker les couleurs des groupes
start = time.time()

# Palette de couleurs pour distinguer les groupes
colors = Category10[10]  # Palette de 10 couleurs

# Optimiser la génération des positions
for i, node_name in enumerate(node_info.keys()):
    # Définir un centre pour chaque groupe sur une grille
    row, col = divmod(i, grid_size)
    center_x = col * padding
    center_y = row * padding

    # Utiliser un spring layout pour positionner les nœuds autour du centre
    group_positions = nx.spring_layout(G.subgraph([node_name]), k=0.5, iterations=50)

    # Décaler les positions du groupe autour de leur centre
    for node, pos in group_positions.items():
        positions[node] = (pos[0] + center_x, pos[1] + center_y)

    # Assigner une couleur à ce groupe
    group_colors[node_name] = colors[i % len(colors)]

end = time.time()
print(f"Temps d'exécution de la partie positions: {end - start:.5f} secondes")

# Vérifier que tous les nœuds ont une couleur, sinon leur assigner une couleur par défaut
default_color = "#808080"  # Gris comme couleur par défaut
for node in G.nodes():
    if node not in group_colors:
        group_colors[node] = default_color

# Récupérer les coordonnées maximales et minimales pour ajuster le cadre
all_x_coords = [pos[0] for pos in positions.values()]
all_y_coords = [pos[1] for pos in positions.values()]

# Déterminer la plage avec un peu de marge (padding)
x_min, x_max = min(all_x_coords) - 1, max(all_x_coords) + 1
y_min, y_max = min(all_y_coords) - 1, max(all_y_coords) + 1

# Création d'un plot Bokeh avec zoom et pan activés
plot = Plot(width=1200, height=800, sizing_mode="stretch_both",
            x_range=Range1d(x_min, x_max), y_range=Range1d(y_min, y_max),
            toolbar_location="right")
plot.title.text = "Graphe interactif par auteur avec zoom"

# Ajout des outils d'interaction : zoom, pan et réinitialisation
plot.add_tools(HoverTool(tooltips=[("Nom", "@index"), ("Infos", "@infos{safe}")]), 
                   TapTool(), BoxZoomTool(), PanTool(), ResetTool(), WheelZoomTool())

# Utiliser le layout personnalisé dans Bokeh
graph_renderer = from_networkx(G, positions)

# Customisation des nœuds : couleurs distinctes par auteur
graph_renderer.node_renderer.data_source.add([group_colors[node] for node in G.nodes()], 'node_color')
graph_renderer.node_renderer.glyph = Circle(radius=0.1, fill_color='node_color')
graph_renderer.node_renderer.selection_glyph = Circle(radius=0.1, fill_color=Spectral4[2])
graph_renderer.node_renderer.hover_glyph = Circle(radius=0.1, fill_color=Spectral4[1])

# Customisation des arêtes
graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=2)
graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=2)

# Politique de sélection et survol
graph_renderer.selection_policy = NodesAndLinkedEdges()
graph_renderer.inspection_policy = NodesAndLinkedEdges()

# Ajouter le rendu du graphe au plot
plot.renderers.append(graph_renderer)
save(plot)

# Afficher le plot
show(plot)
