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
        data.ListeNoeudSettings.forEach((element, index) => {
            const li = document.createElement('li');
            li.className = "color-item";
    
        
            const divColor = document.createElement('input');
            divColor.type = "color";
            divColor.id = `color${index}`;
            divColor.className = 'color-box';
            divColor.value = element.color;
        
            const input = document.createElement('input');
            input.type = 'number';
            input.id = `nb${index}`;
            input.step = 1;
            input.min = 0;
            input.max = 50;
            input.value = element.value;
        
            const p = document.createElement('p')
            p.textContent = element.NoeudsName;
            p.id = `p${index}`;
        
            li.appendChild(p);
            li.appendChild(input);
            li.appendChild(divColor);
        
            divNoeuds.appendChild(li);
        
            input.addEventListener('change', (event) => {
                writeElementNumber(event.target.id, event.target.value);
            });

            divColor.addEventListener('change', (event) => {
                writePickerColor(event.target.id, event.target.value);
            });
        });        

        if (data.TypeChoose === 'Par auteur') {
            
            document.getElementById('DivEnv').style.display = 'none';
            document.getElementById('legend-textEnv').style.display = 'none';
            
            document.getElementById('listeNbNoeuds').style.display = 'none';
            document.getElementById('subtitleParam').style.display = 'none';
            document.getElementById('subtitleColorNodeDOI').style.display = 'none';
            document.getElementById('colorEditNodeDOI').style.display = 'none';
        }

        if (data.TypeChoose === 'Par titre') {
            
            document.getElementById('DivEnv').style.display = 'none';
            document.getElementById('legend-textEnv').style.display = 'none';

            document.getElementById('listeNbNoeuds').style.display = 'none';
            document.getElementById('subtitleParam').style.display = 'none';
            document.getElementById('subtitleColorNodeDOI').style.display = 'none';
            document.getElementById('colorEditNodeDOI').style.display = 'none';
        }

        if (data.TypeChoose === 'Par sujet') {
            document.getElementById('titleEditColor').style.display = 'none';
            document.getElementById('colorEdit').style.display = 'none';
            document.getElementById('subtitleColorNodeDOI').style.display = 'none';
            document.getElementById('colorEditNodeDOI').style.display = 'none';
        }
        
        if (data.TypeChoose === 'Par noeud') {
            document.getElementById('titleEditColor').style.display = 'none';
            document.getElementById('colorEdit').style.display = 'none';
        }
                   

        const ulNode = document.getElementById('ulNode');
        if (data.TypeChoose === 'Par titre' || data.TypeChoose === 'Par auteur' ) {
            // On s'occupe du cas où c'est par titre ou part auteur, pour avoir la couleur des nodes 

            //La div de couleur a changer 
            let divColor = document.getElementById('colorEdit');

            //La couleur stocker dans le json
            let colorNode = data.ColorNodesSpecialType;

            const li = document.createElement('li');
            li.className = "color-item";
            
            divColor.className = 'color-box';
            divColor.value = colorNode;

            li.appendChild(divColor);
            ulNode.appendChild(li);

            //On ajoute un event pour le changement de valeur de la couleur
            divColor.addEventListener('change', (event) => {
                writeColorNodes(event.target.value);
            });

        }
    } else {
        console.error("Impossible de lire les paramètres utilisateur.");
    }
});

function isHexColor(value) {
    const hexColorRegex = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{4}|[0-9A-Fa-f]{8})$/;
    return hexColorRegex.test(value);
}

function writeColorNodes(newColor){
    console.log(newColor,isHexColor(newColor));
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data && isHexColor(newColor)) {
            
            data = JSON.parse(data);
            data.ColorNodesSpecialType = newColor;

            window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                if (err) {
                console.error('Erreur d’écriture :', err);
                }
            });
        }
    });
}

function writePickerColor(elemntId, newColor){
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            data = JSON.parse(data);
            data.ListeNoeudSettings.forEach(element => {
                if (elemntId === "color1" && element.NoeudsName === "Nombre de nodes environnant ") {

                    element.color = newColor;

                    window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                        if (err) {
                        console.error('Erreur d’écriture :', err);
                        }
                    });
                }
                else if (elemntId === "color0" && element.NoeudsName === "Nombre de nodes à l'origine "){
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
    console.log("lgozejgoinbiengpizsr");
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            data = JSON.parse(data);
            data.ColorPickerSettings.forEach(element => {
                if (element.liaisonName === elemntId) {
        
                    element.color = newColor;
                    data.estRecharger = "false";

                    window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                    if (err) {
                    console.error('Erreur d’écriture :', err);
                    }
                    miseAjourTextAjour();

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
                data.estRecharger = "false";

                window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                if (err) {
                console.error('Erreur d’écriture :', err);
                }
                miseAjourTextAjour();

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
            if (elementName === "nb1" && element.NoeudsName === "Nombre de nodes environnant ") {
                if (newValue >=0 && newValue <= 10000 ) 
                {
                    element.value = newValue;
                    data.estRecharger = "false";

                    window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                        if (err) {
                        console.error('Erreur d’écriture :', err);
                        }                   
                        miseAjourTextAjour();
                    });
                }
            }
            else if (elementName === "nb0" && element.NoeudsName === "Nombre de nodes à l'origine "){
                if (newValue >=0 && newValue <= 10000 ) 
                    {
                        element.value = newValue;
                        data.estRecharger = "false";
    
                        window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                            if (err) {
                            console.error('Erreur d’écriture :', err);
                            }                   
                            miseAjourTextAjour();
                        });
                    }
            }
        });
    }
});
}

function miseAjourTextAjour(){
    let texteAjour = document.getElementById("textRefresh");
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            data = JSON.parse(data);
            let estAJour = data.estRecharger;
            // On regarde si il y a besoin de recharger le graphe
            if (estAJour === "false") {
                texteAjour.className = "textEstPasAJour";
                texteAjour.textContent = "Les paramètres et le graphe ne sont pas à jours...";
            }
            else {
                texteAjour.className = "textEstAJour";
                texteAjour.textContent = "Les paramètres et le graphes sont à jours !";
            }
        }
    });
}
miseAjourTextAjour();

const buttonModifCouleurs = document.getElementById('buttonModifCouleurs');
buttonModifCouleurs.onclick = function(){
    // Il ne modifie plus les couleurs mais s'occupe mtn de refresh le graphe si des nouveau paramètre sont activées ou désactivé.

    let estAJour = "false";
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            data = JSON.parse(data);
            estAJour = data.estRecharger;

        // On regarde si il y a besoin de recharger le graphe
        if (estAJour === "false" && data) {

            data.estRecharger = "true";
            window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {
                if (err) {
                console.error('Erreur d’écriture :', err);
                }
            });
            let typeC = "sujet";
            if (data.TypeChoose ==="Par auteur") {
                typeC = "auteur";
            }
            else if (data.TypeChoose ==="Par titre")
            {
                typeC = "titre";
            }
            else if (data.TypeChoose ==="noeud")
                {
                    typeC = "noeud";
                }

            window.api.callFunctionSearch([data.WordChoose, typeC]);

        }
        miseAjourTextAjour();
        }
    });   
    
    

}


