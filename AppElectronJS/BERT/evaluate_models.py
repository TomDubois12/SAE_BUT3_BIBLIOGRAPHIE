import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util

# Charger le modèle
# model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')
model = SentenceTransformer('TomDubois12/fine-tuned-model', token="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")

def evaluate_model(df):
    # Vérifier les colonnes disponibles
    print("Colonnes disponibles dans le DataFrame :")
    print(df.columns)
    
    # Extraire les titres et les résumés des articles valides
    valid_articles = df[['Title', 'Abstract Note']]  # Assurez-vous que ces noms correspondent exactement à vos colonnes

    # Remplacer les valeurs NaN par des chaînes vides
    valid_articles['Abstract Note'] = valid_articles['Abstract Note'].fillna('')

    # Calculer les embeddings pour les titres et résumés
    title_embeddings = model.encode(valid_articles['Title'].tolist(), convert_to_tensor=True)
    abstract_embeddings = model.encode(valid_articles['Abstract Note'].tolist(), convert_to_tensor=True)

    # Initialiser le score
    score = 0
    total_valid_articles = len(valid_articles)

    # Évaluer chaque résumé
    for i in range(total_valid_articles):
        # Calculer les similarités
        similarities = util.pytorch_cos_sim(abstract_embeddings[i], title_embeddings)
        
        # Récupérer l'indice du titre le plus similaire
        most_similar_index = torch.argmax(similarities).item()

        # Vérifier l'indice avant l'accès
        if most_similar_index < total_valid_articles:
            most_similar_title = valid_articles['Title'].iloc[most_similar_index]
            original_index = valid_articles.index[i]
            print(f"Original index for valid article {i}: {original_index}")
            print(f"Most similar index: {most_similar_index} (type: {type(most_similar_index)})")
            print(f"Accessing title with index: {most_similar_index}")

            # Vérifiez si le titre correspond au bon résumé
            if most_similar_index == original_index:
                score += 1
        else:
            print(f"Skipping index {most_similar_index} as it is out of bounds for valid_articles")

    # Calculer le score final
    score_de_correspondance = score / total_valid_articles
    print(f"Score de correspondance : {score_de_correspondance}")
    return score_de_correspondance

# Exemple d'utilisation
if __name__ == "__main__":
    # Remplacez par le chemin vers votre fichier de données
    df = pd.read_csv('Bibliographie.csv')  # Par exemple, 'data/articles.csv'
    score = evaluate_model(df)
