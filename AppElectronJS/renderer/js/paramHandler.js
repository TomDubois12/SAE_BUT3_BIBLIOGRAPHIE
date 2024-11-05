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

            const divColor = document.createElement('div');
            divColor.className = 'color-box';
            divColor.style.backgroundColor = element.color;

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
        });

        /////////////////////////////////
        // La partie pour les nbNoeuds //
        /////////////////////////////////
        const divNoeuds = document.getElementById('listeNbNoeuds');
        data.ListeNoeudSettings.forEach(element => {
            const li = document.createElement('li');
            li.className = "color-item";
            const divColor = document.createElement('div');
            divColor.className = 'color-box';
            divColor.style.backgroundColor = element.color;


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
        });
                   
    } else {
        console.error("Impossible de lire les paramètres utilisateur.");
    }
});


        function writeElementCheck(elementName, newValue){
            window.api.readFile('renderer/json/userSettings.json', (err, data) => {
            if (data) {
                data = JSON.parse(data);
                data.ColorPickerSettings.forEach(element => {
                    if (element.liaisonName === elementName) {
                
                        var nV = ''
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
            console.log('ici');
            window.api.readFile('renderer/json/userSettings.json', (err, data) => {
            if (data) {
                data = JSON.parse(data);
                data.ListeNoeudSettings.forEach(element => {
                    console.log("cc",element.NoeudsName, elementName);
                    if (element.NoeudsName === elementName) {
                
                        if (newValue >=1 && newValue <= 50) 
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