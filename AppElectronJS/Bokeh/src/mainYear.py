import pandas as pd
import networkx as nx
from bokeh.plotting import figure, show, from_networkx, output_file, save
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxZoomTool, PanTool, ResetTool, WheelZoomTool
from bokeh.models.graphs import NodesAndLinkedEdges
from bokeh.embed import components
import json
import numpy as np
import time

# Charger les données
file = '../data/test100.csv'
data2 = pd.read_csv(file)
data = data2.iloc[:, :12]

output_file(filename="../bin/mainYear.html", title="NodeByYear")
# Supprimer les lignes avec des valeurs NaN dans la colonne "Publication Year"
data = data.dropna(subset=["Publication Year"])

# Récupérer toutes les années disponibles dans la colonne "Publication Year"
annees = data["Publication Year"].drop_duplicates().sort_values()

# Déterminer l'année minimale et maximale
annee_min = annees.min()
annee_max = annees.max()

noms = data.iloc[:, 0]
infos = data.iloc[:, 1:4]
annees_data = data["Publication Year"]

# Création du graphe avec NetworkX
G = nx.Graph()

# Pré-calculer les informations pour chaque nœud
start = time.time()
node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
node_year = dict(zip(noms, annees_data))

# Ajouter les nœuds avec les attributs 'infos' et 'year'
G.add_nodes_from([(nom, {'infos': node_info[nom], 'year': node_year[nom]}) for nom in noms])

end = time.time()
print(f"Temps d'exécution de la partie nœuds: {end - start:.5f} secondes")

# Ajouter des liens entre les nœuds de la même année
start = time.time()
grouped_by_annee = data.groupby("Publication Year")[data.columns[0]].apply(list)

for group in grouped_by_annee:
    G.add_edges_from((group[i], group[j]) for i in range(len(group)) for j in range(i + 1, len(group)))

end = time.time()
print(f"Temps d'exécution de la partie arêtes: {end - start:.5f} secondes")

# Définir une grille de positions pour répartir les groupes dans tout l'espace
n_groups = len(annees)
grid_size = int(np.ceil(np.sqrt(n_groups)))  # Taille de la grille pour les centres
padding = 4  # Distance entre les groupes

# Stocker les positions des nœuds
positions = {}
group_colors = {}  # Stocker les couleurs des groupes
start = time.time()

# Créer une fonction pour interpoler la couleur
def interpolate_color(year):
    # Normaliser l'année entre 0 et 1
    year = int(year)
    normalized = (year - annee_min) / (annee_max - annee_min)
    # Calculer la couleur en utilisant une palette de bleu
    r = int(150 - (80 * normalized))  # Red constant
    g = int(200 - (100 * normalized))  # Green constant
    b = int(0 + (200 * normalized))  # Blue variable (de 230 à 0)
    return f"#{r:02x}{g:02x}{b:02x}"

# Optimiser la génération des positions
for i, annee in enumerate(annees):
    row, col = divmod(i, grid_size)
    center_x = col * padding
    center_y = row * padding

    # Récupérer directement les nœuds de l'année courante
    group = grouped_by_annee[annee]

    # Utiliser un spring layout pour positionner les nœuds autour du centre
    group_positions = nx.spring_layout(G.subgraph(group), k=0.5, iterations=50)

    # Décaler les positions du groupe autour de leur centre
    for node, pos in group_positions.items():
        positions[node] = (pos[0] + center_x, pos[1] + center_y)

    # Appliquer l'interpolation de couleur en fonction de l'année
    for node in group:
        group_colors[node] = interpolate_color(node_year[node])

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
plot.title.text = "Graphe interactif par année avec zoom"

# Ajout des outils d'interaction : zoom, pan et réinitialisation
plot.add_tools(HoverTool(tooltips=[("Nom", "@index"), ("Infos", "@infos{safe}")]), 
                   TapTool(), BoxZoomTool(), PanTool(), ResetTool(), WheelZoomTool())

# Utiliser le layout personnalisé dans Bokeh
graph_renderer = from_networkx(G, positions)

# Customisation des nœuds : couleurs distinctes par année
graph_renderer.node_renderer.data_source.add([group_colors[node] for node in G.nodes()], 'node_color')
graph_renderer.node_renderer.glyph = Circle(radius=0.1, fill_color='node_color')
graph_renderer.node_renderer.selection_glyph = Circle(radius=0.1, fill_color="#ff0000")  # Changer la couleur de sélection
graph_renderer.node_renderer.hover_glyph = Circle(radius=0.1, fill_color="#00ff00")  # Changer la couleur de survol

# Customisation des arêtes
graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=1)
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color="#ff0000", line_width=2)  # Changer la couleur de sélection
graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color="#00ff00", line_width=2)  # Changer la couleur de survol

# Politique de sélection et survol
graph_renderer.selection_policy = NodesAndLinkedEdges()
graph_renderer.inspection_policy = NodesAndLinkedEdges()

# Ajouter le rendu du graphe au plot
plot.renderers.append(graph_renderer)
save(plot)
# Afficher le plot
show(plot)

