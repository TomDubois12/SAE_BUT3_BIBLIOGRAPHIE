from sentence_transformers import SentenceTransformer, models, losses
from torch.utils.data import DataLoader
from sentence_transformers import InputExample
import pandas as pd
import torch
import random

# Charger le modèle pré-entraîné
model = SentenceTransformer('sentence-transformers/all-distilroberta-v1')

def prepare_data(file_path, num_negative_pairs=1):
    # Charger les données depuis le fichier CSV avec encodage explicite
    df = pd.read_csv(file_path, encoding='utf-8')

    # Remplacer les valeurs NaN par des chaînes vides
    df['Title'] = df['Title'].fillna('')
    df['Abstract Note'] = df['Abstract Note'].fillna('')

    # Créer des paires de textes (Titre, Abstract)
    pairs = list(zip(df['Title'].tolist(), df['Abstract Note'].tolist()))

    # Créer des paires négatives
    negative_pairs = []
    for _ in range(len(pairs) * num_negative_pairs):
        # Sélectionner un titre et un résumé de manière aléatoire parmi d'autres articles
        random_title = random.choice(df['Title'].tolist())
        random_abstract = random.choice(df['Abstract Note'].tolist())
        negative_pairs.append((random_title, random_abstract))

    # Mélanger les paires positives et négatives
    all_pairs = pairs + negative_pairs
    labels = [1] * len(pairs) + [0] * len(negative_pairs)

    return all_pairs, labels

def fine_tune_model(pairs, labels, epochs=3, batch_size=16, output_dir='fine_tuned_model'):
    # Convertir vos paires en objets InputExample
    train_examples = []
    for i, (title, abstract) in enumerate(pairs):
        train_examples.append(InputExample(texts=[title, abstract], label=labels[i]))

    # Créer un DataLoader pour l'entraînement
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)

    # Définir une fonction de perte (ici la perte de similarité de cosine)
    train_loss = losses.CosineSimilarityLoss(model)

    # Fine-tuning du modèle
    model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=epochs, warmup_steps=100)

    # Sauvegarder le modèle fine-tuné avec save_pretrained
    model.save_pretrained(output_dir)

    print(f"Modèle fine-tuné sauvegardé dans '{output_dir}'")

def main():
    # Remplacez par le chemin vers votre fichier de données
    file_path = 'Bibliographie.csv'  # Par exemple, 'data/articles.csv'
    
    # Préparer les données
    pairs, labels = prepare_data(file_path, num_negative_pairs=2)

    # Fine-tuner le modèle
    fine_tune_model(pairs, labels, epochs=3, batch_size=16, output_dir='fine_tuned_model')

if __name__ == "__main__":
    main()
