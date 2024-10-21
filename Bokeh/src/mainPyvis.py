import json
import numpy as np
import pandas as pd
import networkx as nx
from pyvis.network import Network
# Charger les données
file = '../data/Bibliographie.csv'
data2 = pd.read_csv(file)
data = data2.iloc[:, :12]

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

node_info = {nom: json.dumps(dict(info), ensure_ascii=False) for nom, info in zip(noms, infos.to_dict(orient="records"))}
node_year = dict(zip(noms, annees_data))


G = nx.Graph()
# Ajouter les nœuds avec les attributs 'infos' et 'year'
G.add_nodes_from([(nom, {'infos': node_info[nom], 'year': node_year[nom]}) for nom in noms])

grouped_by_annee = data.groupby("Publication Year")[data.columns[0]].apply(list)
print(grouped_by_annee)
for group in grouped_by_annee:
    G.add_edges_from((group[i], group[j]) for i in range(len(group)) for j in range(i + 1, len(group)))


nt = Network('500px', '500px', notebook=True)
nt.show_buttons(filter_=['physics'])
nt.from_nx(G)
nt.show('../bin/nx.html')