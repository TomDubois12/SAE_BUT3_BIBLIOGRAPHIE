// Assurez-vous que le DOM est complètement chargé avant d'attacher des événements
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener("keydown", function (event) {
        console.log("Touche pressée : ", event.key); // Vérifie si l'événement est détecté
        if (event.key === "Enter") {
            research();
        }
    });
    // Écoute l'événement pour la recherche
    document.getElementById('search-btn').addEventListener('click', async () => {
        const query = document.getElementById('site-search').value; // Récupère la valeur de recherche
        keepResearchParam(query);

        let paramRecherche = "";
        paramRecherche = document.getElementById("listBouton");
        
        console.log(paramRecherche.value)

        const output = await window.api.callFunctionSearch([query, paramRecherche.value]);
    });



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
        boutonADesactiver.style.color = "#166F7A"; // Indique visuellement qu'il est désactivé
    }

    if (boutonAActiver) {
        boutonAActiver.disabled = false;
        boutonAActiver.style.backgroundColor = "#166F7A"; // Indique visuellement qu'il est actif
        boutonAActiver.style.color = "white"; // Indique visuellement qu'il est actif
    }
}

function keepResearchParam(newWord, newType){

    let typeSearch = getSelectedOption()

    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            // On récupère le fichier
            data = JSON.parse(data);

            // On prend le mot actuel et le remplace par le nouveau 
            if (newWord && data.WordChoose)
            {
                data.WordChoose = newWord;
            }
            if (typeSearch && data.TypeChoose)
            {
                data.TypeChoose = typeSearch;
            }
            data.estRecharger = "true";
            // On sauvegarde les modification
            window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {  
            console.error('Erreur d’écriture :', err);
            });
        }
    });


}

function getSelectedOption() {
    // Sélectionne l'élément <select> par son id
    const selectElement = document.getElementById("listBouton");
    
    // Récupère la valeur sélectionnée
    const selectedValue = selectElement.value;
    console.log("Valeur sélectionnée : ", selectedValue);
    
    // Récupère le texte de l'option sélectionnée
    const selectedText = selectElement.options[selectElement.selectedIndex].text;
    return selectedText;
}

async function research(){
    const query = document.getElementById('site-search').value; // Récupère la valeur de recherche
    keepResearchParam(query);

    let paramRecherche = "";
    paramRecherche = document.getElementById("listBouton");
    
    console.log(paramRecherche.value)
    
    const output = await window.api.callFunctionSearch([query, paramRecherche.value]);
}

