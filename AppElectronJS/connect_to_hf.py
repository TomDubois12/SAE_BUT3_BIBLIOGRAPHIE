from huggingface_hub import login, HfApi
from sentence_transformers import SentenceTransformer

# Étape 1 : Connexion à Hugging Face
print("Connexion à Hugging Face...")
login()  # Cela demandera de fournir le token : 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

# Étape 2 : Création du dépôt sur Hugging Face
repo_name = "fine-tuned-model"  # Remplace par le nom souhaité pour le modèle
print(f"Création du dépôt {repo_name} sur Hugging Face...")
api = HfApi()
api.create_repo(repo_name, private=False)  # Change `private=True` si nécessaire
print(f"Le dépôt a été créé : https://huggingface.co/{repo_name}")

# Étape 3 : Push du modèle sur le dépôt
print("Chargement et envoi du modèle vers Hugging Face...")
model = SentenceTransformer("BERT/fine_tuned_model")  # Chemin vers le modèle fine-tuné
model.push_to_hub(repo_name)  # Envoie le modèle sur Hugging Face
print("Modèle poussé avec succès !")

