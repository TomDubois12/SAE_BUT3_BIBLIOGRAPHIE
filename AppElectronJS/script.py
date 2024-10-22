# script.py
import json

def fonction_a(param):
    return json.dumps({"resultat": f"Fonction A a été appelée avec {param}"})

def fonction_b(param1, param2):
    return json.dumps({"resultat": f"Fonction B a été appelée avec {param1} et {param2}"})

if __name__ == "__main__":
    import sys
    func = sys.argv[1]  # Nom de la fonction à appeler
    params = sys.argv[2:]  # Paramètres de la fonction

    if func == 'fonction_a':
        print(fonction_a(params[0]))
    elif func == 'fonction_b':
        print(fonction_b(params[0], params[1]))
