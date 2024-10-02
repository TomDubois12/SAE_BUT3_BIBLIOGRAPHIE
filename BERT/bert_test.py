from transformers import BertTokenizer, BertModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer

# Charger le tokenizer et le modèle BERT
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Fonction pour générer des embeddings de BERT
def get_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze()

# Fonction pour calculer la similarité cosinus avec PyTorch
def cosine_similarity_torch(vec1, vec2):
    cos = torch.nn.functional.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0))
    return cos.item()

# Liste de catégories sans descriptions détaillées
# Liste de catégories avec descriptions
categories = [
    'coiffure: soins capillaires, coupe de cheveux, coloration, salon de coiffure',
    'cuisine: nourriture, recettes, ustensiles, cuisson',
    'construction: bâtiments, poutres, maçonnerie, béton',
    'environnement: forêts, protection de la nature, écologie',
    'technologie: ordinateur, smartphone, internet, logiciel',
    'sport: football, basket, tennis, compétition',
    'voyage: tourisme, avion, destination, exploration',
    'santé: hôpital, médecine, bien-être, nutrition',
    'politique: gouvernement, élections, loi',
    'éducation: école, professeur, apprentissage',
    'musique: instruments, mélodie, concert, artiste',
    'arts: peinture, sculpture, galerie, exposition',
    'économie: argent, banque, marché, finance',
    'science: recherche, théorie, découverte, innovation'
]

# Exemple de texte à classifier
text = """Le piano est un instrument très pertinent dans la musique classique et contemporaine. 
Il est souvent utilisé dans des concerts et des compositions diverses."""

# Fonction pour obtenir les mots importants avec TF-IDF
def get_important_words(text, categories):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([text] + categories)
    feature_names = vectorizer.get_feature_names_out()
    dense = vectors.todense()
    denselist = dense.tolist()
    tfidf_dict = {word: score for word, score in zip(feature_names, denselist[0])}
    return tfidf_dict

# Fonction pour trouver les catégories possibles pour un texte avec les pourcentages
def classify_text(text, categories):
    text_embedding = get_embedding(text)
    category_embeddings = {category: get_embedding(category) for category in categories}
    
    # Calculer la similarité cosinus pour chaque catégorie
    similarities = {category: cosine_similarity_torch(
        text_embedding, 
        category_embedding
    ) for category, category_embedding in category_embeddings.items()}
    
    # Obtenir les mots importants du texte avec TF-IDF
    important_words = get_important_words(text, categories)
    
    # Ajouter du poids basé sur TF-IDF aux similarités cosinus
    adjusted_similarities = {}
    for category, similarity in similarities.items():
        importance_score = sum([important_words.get(word, 0) for word in [category]])
        adjusted_similarities[category] = similarity + importance_score
    
    # Convertir les similarités ajustées en pourcentages
    total_similarity = sum(adjusted_similarities.values())
    percentages = {category: (similarity / total_similarity) * 100 for category, similarity in adjusted_similarities.items()}
    
    # Trier les catégories par pourcentage décroissant
    sorted_percentages = dict(sorted(percentages.items(), key=lambda item: item[1], reverse=True))
    
    return sorted_percentages

# Classifier le texte
result = classify_text(text, categories)

# Afficher les résultats avec les pourcentages
for category, percentage in result.items():
    print(f"Le texte est lié à '{category}' avec une probabilité de {percentage:.2f}%")
