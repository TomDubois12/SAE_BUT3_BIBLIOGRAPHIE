from huggingface_hub import login
from sentence_transformers import SentenceTransformer

# Se connecter à Hugging Face
print("Connexion à Hugging Face...")
login()  # Tu seras invité à entrer ton token d'accès

# Nom du dépôt du modèle Hugging Face (doit déjà exister)
repo_name = "fine-tuned-model"  # Remplace par le nom du dépôt sur Hugging Face

# Charger le modèle fine-tuné depuis le dossier local avec encodage explicite
try:
    print(f"Chargement du modèle depuis {repo_name}...")
    model = SentenceTransformer("BERT/fine_tuned_model")  # Assure-toi que le chemin est correct

    # Pousser le modèle vers Hugging Face
    print(f"Envoi du modèle vers {repo_name} sur Hugging Face...")
    model.push_to_hub(repo_name, commit_message="Initial commit of the fine-tuned model")
    print(f"Modèle envoyé avec succès vers https://huggingface.co/{repo_name}")
except UnicodeDecodeError as e:
    print(f"Erreur d'encodage lors du chargement ou de l'envoi du modèle : {e}")
except Exception as e:
    print(f"Erreur lors de l'envoi du modèle : {e}")




#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
#TomDubois12/fine-tuned-model