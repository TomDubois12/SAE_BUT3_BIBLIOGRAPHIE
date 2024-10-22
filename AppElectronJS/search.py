# search.py
import sys
import json

def search(query):
    # Exemple simple de logique de recherche (vous pouvez la remplacer par une logique réelle)
    result = f"Résultats de la recherche pour '{query}'"
    return json.dumps({"result": result}, ensure_ascii=False)  # Ajout de ensure_ascii=False

if __name__ == "__main__":
    query = sys.argv[1]  # On récupère la requête de recherche transmise en paramètre
    print(query)
    print(search(query))
