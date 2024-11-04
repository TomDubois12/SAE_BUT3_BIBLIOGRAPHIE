#Faire un csv sans doublons


import pandas as pd

# Charger le fichier CSV dans un DataFrame
df = pd.read_csv("BERT/Bibliographie.csv")
df = df.dropna(subset=["DOI"])
# Supprimer les lignes en double en fonction de la colonne "DIO"
df_sans_doublons = df.drop_duplicates(subset="DOI")

# Sauvegarder le DataFrame sans doublons dans un nouveau fichier CSV
df_sans_doublons.to_csv("BERT/Bibliographie_sans_doublon.csv", index=False)