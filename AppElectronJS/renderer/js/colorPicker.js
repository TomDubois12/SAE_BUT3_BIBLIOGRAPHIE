// Sélectionner l'élément du color picker
const colorPicker = document.getElementById('colorPicker');
// Sélectionner l'élément où afficher la couleur sélectionnée
const selectedColor = document.getElementById('selectedColor');


// Ajouter un événement pour détecter le changement de couleur
colorPicker.addEventListener('input', function () {
    // Mettre à jour l'affichage avec la nouvelle couleur sélectionnée
    selectedColor.textContent = colorPicker.value;
    // Vous pouvez également appliquer la couleur à des éléments sur la page
});


const divLiaison = document.getElementById('list-liaison');

function readFile(){
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            data = JSON.parse(data);
            data.ColorPickerSettings.forEach(element => {

                const li = document.createElement('li');

                const nameLiaison = document.createElement('p');
                nameLiaison.textContent = element.liaisonName;
                nameLiaison.className = "color-title";

                const divColor = document.createElement('div');
                divColor.className = 'color-box';
                divColor.style.backgroundColor = element.color; 
                divColor.id = element.liaisonName;
                divColor.className = "color-box";

                const rButton = document.createElement('input');
                rButton.type = 'radio';
                rButton.name = 'select';
                rButton.value = element.liaisonName;
                rButton.id = "idB:"+element.liaisonName;

                li.className = "color-item";
                li.appendChild(nameLiaison);
                li.appendChild(divColor);
                li.appendChild(rButton)
                
                divLiaison.appendChild(li);
            });
            
            const colorItems = document.querySelectorAll('.color-item');
            console.log(colorItems)
            // Ajouter un gestionnaire d'événements à chaque élément <li>
            colorItems.forEach(item => {
                item.addEventListener('click', () => {
                    // Trouver le bouton radio dans cet élément <li> et le cocher
                    const radioButton = item.querySelector('input[type="radio"]');
                    console.log(radioButton);
                    if (radioButton) {
                        radioButton.checked = true; // Coche le bouton radio
                    }
                });
            });
        } else {
            console.error("Impossible de lire les paramètres utilisateur.");
        }
    }); 
}


function getSelectedRadioButton(){

    const selectButtons = document.getElementsByName('select');
    let selectedValue = '';

    // Parcourir les boutons radio pour trouver celui qui est sélectionné
    for (const selectButton of selectButtons) {
        if (selectButton.checked) {
            selectedValue = selectButton.value; // Récupérer la valeur du bouton sélectionné
            break; // Sortir de la boucle une fois trouvé
        }
    }
    return selectedValue;
}



const selectedObject = document.getElementById('selected-object');
function writeFile(){

    // On récupère les settings 
    var data = null;
    window.api.readFile('renderer/json/userSettings.json', (err, fileData) => {
        data = JSON.parse(fileData);
        if (data) {
            // On modifie la couleur de l'element selectioné par la valeur de colorPicker
            data.ColorPickerSettings.forEach(element => {
                if(element.liaisonName === getSelectedRadioButton()){

                    selectedObject.textContent = " Selected object : " + element.liaisonName;
                    element.color = colorPicker.value;
                    const col = document.getElementById(element.liaisonName);
                    col.style.backgroundColor = element.color

                    window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                        if (err) {
                        console.error('Erreur d’écriture :', err);
                        } else {
                        console.log('Écriture réussie');
                        }
                    });
                }
            });
            
        }
    }); 
}

document.addEventListener('DOMContentLoaded', async () => {
    try {
        readFile();
    } catch (error) {
        console.error("Erreur lors de la lecture des paramètres utilisateur :", error);
    }
});







