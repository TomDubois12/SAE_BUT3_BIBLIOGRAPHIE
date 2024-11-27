// Assurez-vous que le DOM est complètement chargé avant d'attacher des événements
document.addEventListener('DOMContentLoaded', () => {

    // Écoute l'événement pour la recherche
    document.getElementById('search-btn').addEventListener('click', async () => {
        const query = document.getElementById('site-search').value; // Récupère la valeur de recherche
        const output = await window.api.callFunctionSearch([query, document.getElementById('auteur').disabled == true]);
        afficherResultat(); // Appelle la fonction pour afficher les résultats
    });

    // Fonction pour afficher le résultat
    function afficherResultat() {
        let filtre = "";
        if (document.getElementById('auteur').disabled) {
            filtre = "sujets";
        } else {
            filtre = "auteurs";
        }
        const inputValue = document.getElementById('site-search').value;
        document.getElementById('result').innerHTML = "Résultat sur les " + filtre + " : " + inputValue;
    }

    // Gestion de l'événement pour la touche "Entrée"
    document.getElementById('site-search').addEventListener('keypress', function(event) {
        if (event.key === "Enter") {
            event.preventDefault(); // Empêche la soumission du formulaire
            afficherResultat(); // Affiche les résultats
        }
    });

    // Active le bouton "Par auteur" par défaut
    desactiverBouton('sujet', 'auteur'); // Appelle la fonction pour désactiver le bouton "sujet"
});

// Fonction pour désactiver un bouton et activer l'autre
function desactiverBouton(idBoutonADesactiver, idBoutonAActiver) {
    const boutonADesactiver = document.getElementById(idBoutonADesactiver);
    const boutonAActiver = document.getElementById(idBoutonAActiver);

    if (boutonADesactiver) {
        boutonADesactiver.disabled = true;
        boutonADesactiver.style.backgroundColor = "white"; // Indique visuellement qu'il est désactivé
        boutonADesactiver.style.color = "black"; // Indique visuellement qu'il est désactivé
    }

    if (boutonAActiver) {
        boutonAActiver.disabled = false;
        boutonAActiver.style.backgroundColor = "#759BFF"; // Indique visuellement qu'il est actif
        boutonAActiver.style.color = "white"; // Indique visuellement qu'il est actif
    }
}
