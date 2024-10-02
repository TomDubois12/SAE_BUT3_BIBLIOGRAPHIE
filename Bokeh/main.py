import pandas as pd
import networkx as nx
from bokeh.plotting import figure, show, from_networkx
from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, TapTool, BoxZoomTool, PanTool, ResetTool
from bokeh.models.graphs import NodesAndLinkedEdges
from bokeh.palettes import Spectral4
from bokeh.embed import components
import json
# Charger les données
file = 'data/test100.csv'
data2 = pd.read_csv(file)
data = data2.iloc[:, :12]


annee = 2014.0
data = data[data["Publication Year"] == annee]

noms = data.iloc[:, 0]
infos = data.iloc[:, 1:4]

print(data)
# Création du graphe avec NetworkX
G = nx.Graph()

# Ajouter un nœud pour chaque nom dans le DataFrame
for i, nom in enumerate(noms):
    info_str = json.dumps(dict(infos.iloc[i]), ensure_ascii=False)  # Convertir les infos en chaîne JSON
    G.add_node(nom, infos=info_str)


# Création d'un plot Bokeh avec zoom et pan activés
plot = Plot(width=1200, height=800, sizing_mode="stretch_both",
            x_range=Range1d(-1.5, 1.5), y_range=Range1d(-1.5, 1.5),
            toolbar_location="right")
plot.title.text = "Graphe interactif avec zoom"

# Ajout des outils d'interaction : zoom, pan et réinitialisation
print(infos)
plot.add_tools(HoverTool(tooltips=[("Nom", "@index"), ("Infos", "@infos{safe}")]), 
               TapTool(), BoxZoomTool(), PanTool(), ResetTool())

# Positionnement des nœuds avec un layout spring (force-directed)
graph_renderer = from_networkx(G, nx.spring_layout, k=1, iterations=1)

# Customisation des nœuds
graph_renderer.node_renderer.glyph = Circle(radius=0.01, fill_color=Spectral4[0])
graph_renderer.node_renderer.selection_glyph = Circle(radius=0.01, fill_color=Spectral4[2])
graph_renderer.node_renderer.hover_glyph = Circle(radius=0.01, fill_color=Spectral4[1])

# Customisation des arêtes
graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=2)
graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=2)
graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=2)

# Politique de sélection et survol
graph_renderer.selection_policy = NodesAndLinkedEdges()
graph_renderer.inspection_policy = NodesAndLinkedEdges()

# Ajouter le rendu du graphe au plot
plot.renderers.append(graph_renderer)

# Génération des composants Bokeh
script, div = components(plot)
#show(plot)
# Étape 3 : Créer la nouvelle structure HTML avec une div personnalisée
custom_html = f"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Bokeh Plot</title>
    <style>
      html, body {{
        box-sizing: border-box;
        display: flow-root;
        height: 100%;
        margin: 0;
        padding: 0;
      }}
    </style>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.5.2.min.js"></script>
    <script type="text/javascript">
        Bokeh.set_log_level("info");
    </script>
  </head>
<body>
    <h1>Mon Graphique</h1>

    {div}  <!-- Insérer la div générée par Bokeh ici -->

    {script}
    
   

</body>
</html>
"""

# Étape 4 : Écrire le contenu dans un fichier HTML
with open('mon_graphique.html', 'w') as f:
    f.write(custom_html)

print("Le fichier 'mon_graphique.html' a été créé avec succès.")
