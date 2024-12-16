const divLiaison = document.getElementById('listeContainer');

window.api.readFile('renderer/json/userSettings.json', (err, data) => {
    if (data) {
        data = JSON.parse(data);

        /////////////////////////////////
        // La partie pour les liaisons //
        /////////////////////////////////
        data.ColorPickerSettings.forEach(element => {
            const li = document.createElement('li');
            li.className = "color-item";


            const divColor = document.createElement('input');
            divColor.type = "color";
            divColor.id = element.liaisonName;
            divColor.className = 'color-box';
            divColor.value = element.color;


            const label = document.createElement('label');

            const input = document.createElement('input');
            input.type = 'checkbox';
            input.id = element.liaisonName;
            input.checked = element.check === 'true';

            label.appendChild(input);
            label.appendChild(document.createTextNode(element.liaisonName));

            li.appendChild(label);
            li.appendChild(divColor);
                    
            divLiaison.appendChild(li);
            input.addEventListener('change', (event) => {
                writeElementCheck(event.target.id,event.target.checked);
            });

            divColor.addEventListener('change',(event) => {
                writeColor(event.target.id, event.target.value);
            })

        });

        /////////////////////////////////
        // La partie pour les nbNoeuds //
        /////////////////////////////////
        const divNoeuds = document.getElementById('listeNbNoeuds');
        data.ListeNoeudSettings.forEach(element => {
            const li = document.createElement('li');
            li.className = "color-item";

            const divColor = document.createElement('input');
            divColor.type = "color";
            divColor.id = element.NoeudsName;
            divColor.className = 'color-box';
            divColor.value = element.color;



            const input = document.createElement('input');
            input.type = 'number';
            input.id = element.NoeudsName;
            input.step = 1;
            input.min = 1;
            input.max = 50;
            input.value = element.value;

            const p = document.createElement('p')
            p.textContent = element.NoeudsName;

            li.appendChild(p);
            li.appendChild(input);
            li.appendChild(divColor);
                    
            divNoeuds.appendChild(li);

            input.addEventListener('change', (event) => {
                writeElementNumber(event.target.id,event.target.value);
            });         
          
            divColor.addEventListener('change',(event) => {
                writePickerColor(event.target.id, event.target.value);
            })

        });
                   
    } else {
        console.error("Impossible de lire les paramètres utilisateur.");
    }
});

function writePickerColor(elemntId, newColor){
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            data = JSON.parse(data);
            data.ListeNoeudSettings.forEach(element => {
                if (element.NoeudsName === elemntId) {
                
                    element.color = newColor;

                    window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                    if (err) {
                    console.error('Erreur d’écriture :', err);
                    }
                });
                }
            });
        }
    });
}

function writeColor(elemntId, newColor){
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            data = JSON.parse(data);
            data.ColorPickerSettings.forEach(element => {
                if (element.liaisonName === elemntId) {
        
                    element.color = newColor;

                    window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                    if (err) {
                    console.error('Erreur d’écriture :', err);
                    }
                });
                }
            });
        }
    });
}


function writeElementCheck(elementName, newValue){
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
    if (data) {
        data = JSON.parse(data);
        data.ColorPickerSettings.forEach(element => {
            if (element.liaisonName === elementName) {
        
                let nV = ''
                if (newValue){nV = 'true';} else{ nV = 'false';}
                element.check = nV;

                window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                if (err) {
                console.error('Erreur d’écriture :', err);
                }
            });
            }
        });
    }
});
}

function writeElementNumber(elementName, newValue){
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
    if (data) {
        data = JSON.parse(data);
        data.ListeNoeudSettings.forEach(element => {

            if (element.NoeudsName === elementName) {
        
                if (newValue >=1 && newValue <= 10000 ) 
                {
                    element.value = newValue;

                window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                if (err) {
                console.error('Erreur d’écriture :', err);
                }
            });
                }
            }
        });
    }
});
}

const buttonModifCouleurs = document.getElementById('buttonModifCouleurs');
buttonModifCouleurs.onclick = function(){
    window.api.openWindoColor();
}
