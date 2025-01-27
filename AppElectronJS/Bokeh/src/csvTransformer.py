#Faire un csv sans doublons
import pandas as pd
import numpy as np
import os
import sys


bert_path = os.path.join(current_dir, '..', '..', 'BERT')
if os.path.isdir(bert_path) and bert_path not in sys.path:
    sys.path.append(bert_path)


def createBy_dropna_and_duplicate():
    # Charger le fichier CSV dans un DataFrame
    df = pd.read_csv(bert_path + "/Bibliographie.csv")
    df = df.dropna(subset=["DOI"])
    # Supprimer les lignes en double en fonction de la colonne "DIO"
    df_sans_doublons = df.drop_duplicates(subset="DOI")

    # Sauvegarder le DataFrame sans doublons dans un nouveau fichier CSV
    df_sans_doublons.to_csv( bert_path+"/Bibliographie_sans_doublon.csv", index=False)

def addNbCitation():
    df = pd.read_csv(bert_path + "/Bibliographie_sans_doublon.csv")

    # Ajouter la colonne "nbCitation" avec des valeurs aléatoires entre 0 et 1000
    df['nbCitation'] = np.random.randint(0, 1001, size=len(df))

    # Enregistrer le DataFrame modifié dans un nouveau fichier CSV ou remplacer l'ancien fichier
    df.to_csv(bert_path +"/Bibliographie_sans_doublon.csv", index=False)



if __name__ == "__main__":
    addNbCitation()