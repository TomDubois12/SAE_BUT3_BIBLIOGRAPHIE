import json
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network
from BERT.test import search_by_keyword

# Charger les données
file = 'Bokeh/data/Bibliographie.csv'
data2 = pd.read_csv(file)
data = data2.iloc[:, :12]

# Définir la colonne "Key" comme index
data.set_index("Key", inplace=True)

# Supprimer les lignes avec des valeurs NaN dans la colonne "Publication Year"
data = data.dropna(subset=["Publication Year"])

noms = data.index  # Accéder à l'index au lieu de la colonne "Key"
infos = data.iloc[:, 0:3]  # Prendre les infos (les colonnes restantes)
annees_data = data["Publication Year"]

# Rechercher par mot clé
mot_cle = "Linear sweep voltammetry at very small stationary disk electrodes"
res = search_by_keyword(mot_cle)

# Extraire les clés de la recherche
liste_cles = [cle for cle, valeur in res]

# Reindexer le DataFrame selon les clés trouvées
dfFinal = data.reindex(liste_cles)

noms = dfFinal.index  # Utiliser l'index (les clés)
infos = dfFinal.iloc[:, 0:3]  # Prendre les colonnes qui contiennent les informations

print(noms, infos)

# Créer un dictionnaire d'informations pour les nœuds
node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
node_year = dict(zip(noms, annees_data.reindex(noms)))  # Reindexer les années pour qu'elles correspondent aux clés/noms

# Créer le graphe
G = nx.Graph()

# Ajouter les nœuds avec les attributs 'infos' et 'year'
G.add_nodes_from([(nom, {'infos': node_info[nom], 'year': node_year[nom]}) for nom in noms])

# Grouper par année et ajouter les arêtes
grouped_by_annee = dfFinal.groupby("Publication Year").apply(lambda x: list(x.index))  # Utiliser l'index ici
print(grouped_by_annee)

for group in grouped_by_annee:
    G.add_edges_from((group[i], group[j]) for i in range(len(group)) for j in range(i + 1, len(group)))

# Visualiser avec PyVis
nt = Network('500px', '500px', notebook=True)
nt.show_buttons(filter_=['physics'])
nt.from_nx(G)
nt.show('Bokeh/bin/nx.html')
