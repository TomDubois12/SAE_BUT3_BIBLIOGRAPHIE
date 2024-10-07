import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Charger le modèle pré-entraîné
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Charger le fichier CSV (ex: 'articles.csv'), où la colonne des abstracts s'appelle 'Abstract Note'
df = pd.read_csv('Bibliographie.csv')

# Vérifier les premières lignes du DataFrame pour confirmer les colonnes
print(df.head())

# Extraire les colonnes 'Key' et 'Abstract Note' (résumés des articles)
keys = df['Key'].dropna().tolist()  # On retire les valeurs manquantes (NaN) pour les clés
abstracts = df['Abstract Note'].dropna().tolist()  # On retire les valeurs manquantes (NaN)

# Mot clé pour la recherche
mot_cle = "netron"

# Générer les embeddings pour les abstracts et le mot clé
abstract_embeddings = model.encode(abstracts)
mot_cle_embedding = model.encode(mot_cle)

# Calculer la similarité entre le mot clé et chaque abstract
similarities = util.cos_sim(mot_cle_embedding, abstract_embeddings)

# Associer les similarités aux abstracts et aux clés
similarities_with_abstracts = list(zip(keys, abstracts, similarities[0].tolist()))

# Trier les abstracts par ordre décroissant de similarité
similarities_with_abstracts.sort(key=lambda x: x[2], reverse=True)

# Afficher les 15 abstracts les plus proches du mot clé avec leur Key
print(f"Top 15 résultats pour le mot clé '{mot_cle}':\n")
for key, abstract, score in similarities_with_abstracts[:15]:
    print(f"Key: {key} \nAbstract: {abstract} \nSimilarité: {score:.4f}\n")
