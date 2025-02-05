/*
 * Crédits :
 * - Auteur : IUT Orléans Département Informatique
 * - Collaborateurs : BOISSAY Robin, BOISSAY Nathan, BRION Adèle, DUBOIS Tom
 * - Date de création : 11 septembre 2024
 * - Version : 1.0
 * - Description : Ce fichier sert à la gestion des clics sur le graphe
 *
 * Remerciements à CLEUZIOU Guillaume.
 */

let AS_ASIDE = false;
let AS_CLICK = false;
let idSelectedNode = "";

async function changeColorOnHover(nodeId, isOrigin) {

    // Obtenir la couleur associée au nœud (origine ou non)
    let color;

    let year = network.body.data.nodes.get(nodeId).year;
    let minD;
    let maxD;
    if (isOrigin) {
        minD = minDateOrigin;
        maxD = maxDateOrigin;
    } else {
        minD = minDateEnv;
        maxD = maxDateEnv;
    }
    if (network.body.data.nodes.get(nodeId).primaryNode) {
        color = await getColorOrigineArticle();
        network.body.data.nodes.update({
            id: nodeId,
            color: getColorForDate(year, maxD, minD, color),
            borderWidth: 5,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.7)', size: 8, x: 5, y: 5 },
        });
    } else {
        color = await getColorParamUser(isOrigin);
        network.body.data.nodes.update({
            id: nodeId,
            color: getColorForDate(year, maxD, minD, color),
            borderWidth: 4,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 5, x: 2, y: 2 },
        });
    }


}

async function changeBlurColor(nodeId, isOrigin) {

    if (nodeId == idSelectedNode) { return; }
    // Obtenir la couleur associée au nœud (origine ou non)
    let color;

    let year = network.body.data.nodes.get(nodeId).year;
    let minD;
    let maxD;
    if (isOrigin) {
        minD = minDateOrigin;
        maxD = maxDateOrigin;
    } else {
        minD = minDateEnv;
        maxD = maxDateEnv;
    }
    if (network.body.data.nodes.get(nodeId).primaryNode) {
        color = await getColorOrigineArticle();
        network.body.data.nodes.update({
            id: nodeId,
            color: getColorForDate(year, maxD, minD, color),
            borderWidth: 5,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.7)', size: 8, x: 5, y: 5 },
        });
    } else {
        color = await getColorParamUser(isOrigin)
        network.body.data.nodes.update({
            id: nodeId,
            color: getColorForDate(year, maxD, minD, color),
            borderWidth: 1,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 5, x: 2, y: 2 },
        });
    }
}

async function changeColorOnClick(nodeId) {

    const isOrigin = network.body.data.nodes.get(nodeId).isOrigin;
    let color;
    let year = network.body.data.nodes.get(nodeId).year;
    let minD;
    let maxD;
    if (isOrigin) {
        minD = minDateOrigin;
        maxD = maxDateOrigin;
    } else {
        minD = minDateEnv;
        maxD = maxDateEnv;
    }
    if (network.body.data.nodes.get(nodeId).primaryNode) {
        color = await getColorOrigineArticle();
        network.body.data.nodes.update({
            id: nodeId,
            color: getColorForDate(year, maxD, minD, color),
            borderWidth: 5,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.7)', size: 8, x: 5, y: 5 },
        });
    } else {
        color = await getColorParamUser(isOrigin);
        network.body.data.nodes.update({
            id: nodeId,
            color: getColorForDate(year, maxD, minD, color),
            borderWidth: 3,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 5, x: 2, y: 2 },
        });
    }
}

async function colorOnNodeSave(idNode) {

    if (idNode === "") { return; }

    const isOrigin = network.body.data.nodes.get(idNode).isOrigin;
    let color;

    let year = network.body.data.nodes.get(idNode).year;
    let minD;
    let maxD;
    if (isOrigin) {
        minD = minDateOrigin;
        maxD = maxDateOrigin;
    } else {
        minD = minDateEnv;
        maxD = maxDateEnv;
    }
    if (network.body.data.nodes.get(idNode).primaryNode) {
        color = await getColorOrigineArticle();
        network.body.data.nodes.update({
            id: idNode,
            color: getColorForDate(year, maxD, minD, color),
            borderWidth: 5,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.7)', size: 8, x: 5, y: 5 },
        });
    } else {
        color = await getColorParamUser(isOrigin);
        network.body.data.nodes.update({
            id: idNode,
            color: getColorForDate(year, maxD, minD, color),
            borderWidth: 1,
            shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 10, x: 5, y: 5 },
        });
    }
    if (idSelectedNode == nodeId) {
        idSelectedNode = "";
    }
}

function removeAsideOnNeutralClick() {
    const className = 'generated-div';
    const existingElements = document.getElementsByClassName(className);
    if (existingElements.length > 0) {
        existingElements[0].remove();
        AS_ASIDE = false;
    }
}

function createAside(nodeId) {
    if (!nodeId) return null;

    const canva = document.getElementsByClassName('contenerCanvaAside')[0];
    const className = 'generated-div';

    // Récupération des données du nœud
    const nodeData = network.body.data.nodes.get(nodeId);

    // Recherche de l'aside déjà existant
    const existingAside = document.getElementById(nodeId);

    if (existingAside) {
        // Si l'aside existe déjà pour ce nodeId, on arrête la fonction
        return;
    } else {
        // Supprimer tous les autres éléments aside sauf celui de la node sélectionnée
        const existingElements = document.getElementsByClassName(className);
        if (existingElements.length > 0) {
            existingElements[0].remove();
        }

        // Création d'un nouvel élément aside
        const aside = document.createElement("aside");

        // Ajout du contenu à l'aside avec titre, auteur, année, etc.
        const titre = document.createElement("h1");
        titre.classList.add("pTitle");
        titre.textContent = `Titre de la publication : ${nodeData.title || "Titre non disponible"}`;
        aside.appendChild(titre);

        const author = document.createElement("p");
        author.classList.add("pAuthor");
        author.textContent = `Auteur(s), co-auteur(s) : ${nodeData.author || "Auteur(s) non disponible"}`;
        aside.appendChild(author);

        const year = document.createElement("p");
        year.classList.add("pYear");
        year.textContent = `Année de publication : ${nodeData.year || "Année non disponible"}`;
        aside.appendChild(year);

        const nb_citation = document.createElement("p");
        nb_citation.classList.add("pCitation");
        nb_citation.textContent = `Nombre de citations : ${nodeData.nb_citations || "Nombre de citation non disponible"}`;
        aside.appendChild(nb_citation);

        const abstract = document.createElement("p");
        abstract.classList.add("pAbstract");
        abstract.textContent = `Abstract : ${nodeData.abstract || "Abstract non disponible"}`;
        aside.appendChild(abstract);

        const doi = document.createElement("button");
        doi.classList.add("pDOI");
        doi.textContent = `Ouvrir le lien`;

        // Check if DOI or citation link is available
        if (nodeData.url) {
            doi.addEventListener('click', () => {
                window.open(nodeData.url, "_blank", "noopener noreferrer");
            });
        } else {
            doi.setAttribute('disabled', true);  // Disable button if no citation
        }

        aside.appendChild(doi);
        const buttonCreateGraph = document.createElement("button");
        buttonCreateGraph.textContent = "Générer le graphe de cet article"
        buttonCreateGraph.classList.add("buttonGenerateGraph");
        buttonCreateGraph.addEventListener("click", async (e) => {
            window.api.readFile('renderer/json/userSettings.json', (err, data) => {
                if (data) {
                    data = JSON.parse(data);
                    data.WordChoose = nodeData.doi;
                    data.TypeChoose = "Par doi";
                    window.api.writeFile('renderer/json/userSettings.json', JSON.stringify(data), (err) => {
                        if (err) {
                            console.error('Erreur d’écriture :', err);
                        }
                    });
                }
            });

            let divInvisible = document.getElementsByClassName("divInvisible")[0];
            divInvisible.classList.add("invisibleBackground");
            divInvisible.style.visibility = "visible";
            const output = await window.api.callFunctionSearch([nodeData.doi, "noeud"]);  // si on veut ajouter une nouvelle page, on rajoute true dans la liste
            divInvisible.classList.remove("invisibleBackground");
            divInvisible.style.visibility = "hidden";
        });

        window.api.readFile('renderer/json/userSettings.json', (err, data) => {
            if (data) {
                data = JSON.parse(data);
                data.asideDOI = nodeData.doi;
                window.api.writeFile('renderer/json/userSettings.json', JSON.stringify(data), (err) => {
                    if (err) {
                        console.error('Erreur d’écriture :', err);
                    }
                });
            }
        });


        aside.appendChild(buttonCreateGraph);

        aside.classList.add(className);
        aside.id = nodeId;

        // Ajouter l'aside au DOM
        AS_ASIDE = true;
        canva.appendChild(aside);
    }
}

function onClick(params) {

    const nodeId = params.nodes[0];
    if (!nodeId) {
        AS_CLICK = false;
        colorOnNodeSave(idSelectedNode); // réinitialise la couleur de la dernière sélection
        removeAsideOnNeutralClick(); // cache le aside
        return;
    }

    // Vérifie si l'aside pour ce nodeId est déjà affiché avant de le créer
    const existingAside = document.getElementById(nodeId);
    if (!existingAside) {
        createAside(nodeId);
    }
    // Pour bloquer l'apparition de hover quand une est cliqué

    // Changer la couleur du nœud sur le clic
    if (nodeId !== idSelectedNode) {
        // Sauvegarde la couleur de l'ancien nœud
        colorOnNodeSave(idSelectedNode);
        idSelectedNode = nodeId; // met à jour le nœud sélectionné
    }


    AS_CLICK = true;
    changeColorOnClick(nodeId);
}

function onHover(params) {
    const nodeId = params.node;
    if (!AS_CLICK) {
        createAside(nodeId)
    }
    changeColorOnHover(nodeId, network.body.data.nodes.get(nodeId).isOrigin);

}

function onBLur(params) {
    const nodeId = params.node;
    if (!AS_CLICK) {
        changeBlurColor(nodeId, network.body.data.nodes.get(nodeId).isOrigin);
    } else {
        if (nodeId !== idSelectedNode) {
            changeBlurColor(nodeId, network.body.data.nodes.get(nodeId).isOrigin);
        }
    }
}


function getColorParamUser(isOrigin) {
    return new Promise((resolve, reject) => {
        window.api.readFile('renderer/json/userSettings.json', (err, data) => {
            if (err) {
                console.error('Erreur lors de la lecture du fichier JSON:', err);
                reject('Erreur lors de la lecture du fichier');
                return;
            }

            try {
                data = JSON.parse(data);  // Conversion du JSON en objet JavaScript

                // Initialisation de la couleur par défaut
                let colorToReturn = "#000000";

                // Si recherche par auteur ou titre, on renvoi la couleur unique
                if (data.TypeChoose === "Par titre" || data.TypeChoose === "Par auteur") {
                    colorToReturn = data.ColorNodesSpecialType;
                    resolve(colorToReturn);  // Résoudre avec la couleur appropriée
                }

                // Sinon on cherche il faut laquelle
                // Recherche dans "ListeNoeudSettings" en fonction de la propriété isOrigin
                if (isOrigin) {
                    // Trouver la couleur pour le nœud à l'origine
                    const origineNode = data.ListeNoeudSettings.find(
                        element => element.NoeudsName === "Nombre de nodes à l'origine "
                    );
                    if (origineNode && origineNode.color) {
                        colorToReturn = origineNode.color;
                    }
                } else {
                    // Trouver la couleur pour les nœuds environnants
                    const surroundingNode = data.ListeNoeudSettings.find(
                        element => element.NoeudsName === "Nombre de nodes environnant "
                    );
                    if (surroundingNode && surroundingNode.color) {
                        colorToReturn = surroundingNode.color;
                    }
                }

                resolve(colorToReturn);  // Résoudre avec la couleur appropriée
            } catch (parseError) {
                console.error('Erreur de parsing JSON:', parseError);
                reject('Erreur lors du parsing du fichier JSON');
            }
        });
    });
}
function getColorOrigineArticle() {
    return new Promise((resolve, reject) => {
        window.api.readFile('renderer/json/userSettings.json', (err, data) => {
            if (err) {
                console.error('Erreur lors de la lecture du fichier JSON:', err);
                reject('Erreur lors de la lecture du fichier');
                return;
            }

            try {
                data = JSON.parse(data);  // Conversion du JSON en objet JavaScript
                resolve(data.ColorOriginArticle);  // Résoudre avec la couleur appropriée
            } catch (parseError) {
                console.error('Erreur de parsing JSON:', parseError);
                reject('Erreur lors du parsing du fichier JSON');
            }
        });
    });
}

network.on("click", onClick);
network.on("hoverNode", onHover);
network.on("blurNode", onBLur);
network.on("hoverEdge", function (params) {
    const suiviSouris = document.getElementById('suivi-souris');

    suiviSouris.style.left = event.pageX - suiviSouris.offsetWidth / 2 + 'px';
    suiviSouris.style.top = event.pageY - suiviSouris.offsetHeight / 2 + 'px';
    suiviSouris.style.display = "block";
    const edgeId = params.edge; // ID de l'edge survolé
    let texte = network.body.data.edges.get(edgeId).title;
    if (isNaN(texte)) {
        suiviSouris.style.display = "none";
    }
    if (texte < 0) { texte = 0; }
    texte = Math.round(texte * 100) + "%";
    suiviSouris.textContent = texte;


});

network.on("blurEdge", function (params) {
    const suiviSouris = document.getElementById('suivi-souris');

    // Cacher l'élément de suivi de la souris
    suiviSouris.style.display = "none";
});

function adjustColorBrightness(hex, factor) {
    // Enlever le "#" du début si nécessaire
    hex = hex.replace('#', '');

    // Convertir la couleur hex en RGB
    let r = parseInt(hex.substring(0, 2), 16);
    let g = parseInt(hex.substring(2, 4), 16);
    let b = parseInt(hex.substring(4, 6), 16);

    // Ajuster la luminosité en fonction du facteur (valeur de 0 à 1)
    r = Math.min(255, Math.max(0, r + factor * (255 - r)));
    g = Math.min(255, Math.max(0, g + factor * (255 - g)));
    b = Math.min(255, Math.max(0, b + factor * (255 - b)));

    // Convertir à nouveau en hexadécimal
    return `#${((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1).toUpperCase()}`;
}

function getColorForDate(date, minDate, maxDate, baseColor) {
    //function getColorForDate(date, minDate = 1984, maxDate = 2015, baseColor = '#A62121') {
    // Normaliser l'année dans la plage de 0 à 1
    const normalizedYear = (date - minDate) / (maxDate - minDate);
    if (isNaN(normalizedYear)) {
        return adjustColorBrightness(baseColor, 0.2);
    }
    // Calculer la luminosité en fonction de l'année : plus près de 1984, plus foncé, plus près de 2015, plus clair
    const factor = normalizedYear * 0.5; // Ajuste le facteur si nécessaire

    // Retourner la couleur ajustée
    return adjustColorBrightness(baseColor, factor);
}

let maxDateOrigin;
let minDateOrigin;
let maxDateEnv;
let minDateEnv;

function loadNodesColor() {
    network.body.data.nodes.forEach((elem) => {
        const isOrigin = elem.isOrigin;
        if (isOrigin) {
            // Si le nœud est d'origine
            if (maxDateOrigin == null || elem.year > maxDateOrigin) {
                maxDateOrigin = elem.year;
            }
            if (minDateOrigin == null || elem.year < minDateOrigin) {
                minDateOrigin = elem.year;
            }
        } else {
            // Si le nœud n'est pas d'origine (environnement)
            if (maxDateEnv == null || elem.year > maxDateEnv) {
                maxDateEnv = elem.year;
            }
            if (minDateEnv == null || elem.year < minDateEnv) {
                minDateEnv = elem.year;
            }
        }
    });
}
loadNodesColor();


function addDynamicCSS() {
    const style = document.createElement('style');
    style.textContent = `
        .dynamic-div {
            width: 300px;
            height: 20px;
            display: flex;
            align-items: center; /* Centre verticalement */
            justify-content: flex-end; /* Aligne à droite */
            border: 1px solid black;
            border-radius: 2px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .legend {
            font-family: Arial, sans-serif;
            font-size: 14px;
            text-align: center;
            margin-top: 10px;
        }
    `;
    document.head.appendChild(style); // Ajoute le style dans <head>
}

async function setAllNodeDeg() {
    // Mettre à jour les nœuds
    network.body.data.nodes.forEach(async (elem) => {
        try {
            const isOrigin = elem.isOrigin;
            let color;

            const { minD, maxD } = getDateRange(isOrigin);
            if (elem.primaryNode) {

                color = await getColorOrigineArticle()
                network.body.data.nodes.update({
                    id: elem.id,
                    color: getColorForDate(elem.year, maxD, minD, color),
                    borderWidth: 5,
                    shadow: { enabled: true, color: 'rgba(0,0,0,0.7', size: 10, x: 7, y: 7 },
                });
            } else {
                color = await getColorParamUser(isOrigin)
                network.body.data.nodes.update({
                    id: elem.id,
                    color: getColorForDate(elem.year, maxD, minD, color),
                    borderWidth: 1,
                    shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 10, x: 5, y: 5 },
                });
            }
        } catch (error) {
            console.error(`Error updating node ${elem.id}:`, error);
        }
    });

    // Appliquer le gradient et la légende
    try {


        const colorOrigin = await getColorParamUser(true);
        const colorEnv = await getColorParamUser(false);



        const DivOrigine = document.getElementById("DivOrigin");
        DivOrigine.classList.add('dynamic-div');

        const colorOrMin = getColorForDate(maxDateOrigin, maxDateOrigin, minDateOrigin, colorOrigin);
        const colorOrMax = getColorForDate(minDateOrigin, maxDateOrigin, minDateOrigin, colorOrigin);


        DivOrigine.style.background = `linear-gradient(to left, ${colorOrMin}, ${colorOrMax})`;

        const legend = document.getElementById("legend-textOr");
        if (minDateOrigin === undefined || maxDateOrigin === undefined) {
            legend.textContent = "Node manquante";
            document.getElementById('DivOrigin').style.display = 'none';
            document.getElementById('legend-textOr').style.display = 'none';
        } else {
            legend.textContent = `Date allant de (${minDateOrigin} → ${maxDateOrigin})`;
        }

        const colorEnvMin = getColorForDate(maxDateEnv, maxDateEnv, minDateEnv, colorEnv);
        const colorEnvMax = getColorForDate(minDateEnv, maxDateEnv, minDateEnv, colorEnv);

        const DivEnv = document.getElementById("DivEnv");
        DivEnv.classList.add('dynamic-div');

        DivEnv.style.background = `linear-gradient(to left, ${colorEnvMin}, ${colorEnvMax})`;

        const legendE = document.getElementById("legend-textEnv");
        if (minDateEnv === undefined || maxDateEnv === undefined) {
            legendE.textContent = "Node manquante";
            document.getElementById('DivEnv').style.display = 'none';
            document.getElementById('legend-textEnv').style.display = 'none';
        } else {
            legendE.textContent = `Date allant de (${minDateEnv} → ${maxDateEnv})`;
        }

        let minSizeNode = null;
        let minRefNode = null;
        let maxSizeNode = null;
        let maxRefNode = null;
        network.body.data.nodes.forEach(node => {
            console.log(node);
            nb_citations = node.nb_citations;
            if (minRefNode === null || nb_citations < minRefNode) {
                minSizeNode = node.size;
                minRefNode = nb_citations;

            }
            if (maxRefNode === null || nb_citations > maxRefNode) {
                maxSizeNode = node.size;
                maxRefNode = nb_citations
            }
        });





        const legendNodeMinText = document.querySelector(".nodeMinText");
        legendNodeMinText.textContent = minRefNode;
        const legendNodeMinSize = document.querySelector(".nodeMin");
        legendNodeMinSize.style.width = minSizeNode + "px";
        legendNodeMinSize.style.height = minSizeNode + "px";
        if (maxRefNode !== minRefNode) {
            const legendNodeMaxText = document.querySelector(".nodeMaxText");
            legendNodeMaxText.textContent = maxRefNode;

            const legendNodeMaxSize = document.querySelector(".nodeMax");
            legendNodeMaxSize.style.width = maxSizeNode + "px";
            legendNodeMaxSize.style.height = maxSizeNode + "px";
        }

        console.log(minSizeNode);
        console.log(maxSizeNode);

        addDynamicCSS()
    } catch (error) {
        console.error("Error applying gradient or legend:", error);
    }
}

// Fonction utilitaire pour obtenir les plages de dates
function getDateRange(isOrigin) {
    return isOrigin
        ? { minD: minDateOrigin, maxD: maxDateOrigin }
        : { minD: minDateEnv, maxD: maxDateEnv };
}

setAllNodeDeg();


function updateNetworkOptions(newOptions) {
    network.setOptions(newOptions);
}

// Exemple : Désactiver la physique du réseau après un certain événement
updateNetworkOptions({
    "interaction": {
        "hover": true
    },
});


// Fonction pour initialiser l'écouteur d'événement sur l'élément quand il est trouvé
function initializeColorChangeListener() {

    // Filtrer pour trouver celui avec le bon ID

    const colorOrigineChange = document.getElementById("color0");
    const colorEnvironChange = document.getElementById("color1");
    const colorNodeChange = document.getElementById("colorEdit");
    const colorOriginNodeChange = document.getElementById("colorEditNodeDOI");

    if (colorOrigineChange) {  // Si l'élément est trouvé
        colorOrigineChange.addEventListener('change', (event) => {
            if (window.api && typeof window.api.reloadGraph === 'function') {
                setTimeout(() => {
                    window.api.reloadGraph();
                }, 250);
            } else {
                console.error("window.api.reloadGraph n'est pas disponible.");
            }
        });
        // Une fois trouvé et l'écouteur ajouté, on arrête l'observation
        observer.disconnect();
    }

    if (colorEnvironChange) {  // Si l'élément est trouvé
        colorEnvironChange.addEventListener('change', (event) => {
            if (window.api && typeof window.api.reloadGraph === 'function') {
                setTimeout(() => {
                    window.api.reloadGraph();
                }, 250);
            } else {
                console.error("window.api.reloadGraph n'est pas disponible.");
            }
        });
        // Une fois trouvé et l'écouteur ajouté, on arrête l'observation
        observer.disconnect();
    }
    if (colorNodeChange) {  // Si l'élément est trouvé
        colorNodeChange.addEventListener('change', (event) => {
            if (window.api && typeof window.api.reloadGraph === 'function') {
                setTimeout(() => {
                    window.api.reloadGraph();
                }, 250);
            } else {
                console.error("window.api.reloadGraph n'est pas disponible.");
            }
        });
        // Une fois trouvé et l'écouteur ajouté, on arrête l'observation
        observer.disconnect();
    }

    if (colorOriginNodeChange) {  // Si l'élément est trouvé
        colorOriginNodeChange.addEventListener('change', (event) => {

            if (window.api && typeof window.api.reloadGraph === 'function') {
                setTimeout(() => {
                    window.api.reloadGraph();
                }, 250);
            } else {
                console.error("window.api.reloadGraph n'est pas disponible.");
            }
        });
        // Une fois trouvé et l'écouteur ajouté, on arrête l'observation
        observer.disconnect();
    }


}

// Créer un observer pour surveiller les modifications dans le DOM
const observer = new MutationObserver((mutationsList, observer) => {
    for (const mutation of mutationsList) {
        if (mutation.type === 'childList') {
            initializeColorChangeListener();  // Tente de lier l'écouteur dès qu'un nouveau nœud est ajouté
        }
    }
});

// Configurer l'observer pour surveiller les ajouts d'éléments enfants dans tout le document
observer.observe(document.body, { childList: true, subtree: true });

// Appel initial pour vérifier si l'élément existe déjà
setTimeout(() => {
    initializeColorChangeListener();
}, 500);



function lightenColor(hexColor, factor = 0.5) {
    // Vérifie si la couleur est bien au format hexadécimal à 6 caractères
    if (!/^#([0-9A-F]{3}){1,2}$/i.test(hexColor)) {
        throw new Error('Couleur hexadécimale invalide');
    }

    // Convertir la couleur hexadécimale en composants RGB
    let color = hexColor.substring(1);  // Retirer le #
    if (color.length === 3) {  // Format court #RGB
        color = color.split('').map(c => c + c).join('');  // Convertit en format #RRGGBB
    }
    const num = parseInt(color, 16);

    // Extraire les valeurs RGB
    let r = (num >> 16) & 255;
    let g = (num >> 8) & 255;
    let b = num & 255;

    // Appliquer le facteur d'éclaircissement, en ajoutant une proportion de la distance jusqu'à 255
    r = Math.min(255, Math.floor(r + (255 - r) * factor));
    g = Math.min(255, Math.floor(g + (255 - g) * factor));
    b = Math.min(255, Math.floor(b + (255 - b) * factor));

    // Convertir les valeurs RGB en couleur hexadécimale
    const lightenedColor = `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`;
    return lightenedColor;
}


// On remet la valeur de la bar de recherche 
// Init la valeur de la bar de recherche 
function setWordSearch() {
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            // On récupère le fichier
            data = JSON.parse(data);
            document.getElementById('site-search').value = data.WordChoose;


            // Mettre le type de recherche 
            const selectElement = document.getElementById("listBouton");
            if (data.TypeChoose && data.TypeChoose === "Par auteur") {
                selectElement.value = "auteur";
            }
            else if ((data.TypeChoose && data.TypeChoose === "Par titre")) {
                selectElement.value = "titre";
            }
            else if ((data.TypeChoose && data.TypeChoose === "Par sujet")) {
                selectElement.value = "sujet";
            }
            else if ((data.TypeChoose && data.TypeChoose === "Par doi")) {
                selectElement.value = "noeud";
            }
            else if ((data.TypeChoose && data.TypeChoose === "Par reference")) {
                selectElement.value = "reference";
            }
        }
    });
}
setWordSearch();


function setTextAJour() {
    let texteAjour = document.getElementById("textRefresh");
    let estAJour;

    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            // On récupère le fichier
            data = JSON.parse(data);
            estAJour = data.estRecharger;
            if (estAJour === "true") {
                texteAjour.textContent = "Les paramètres et le graphes sont à jours !";
            }
            else {
                texteAjour.textContent = "Les paramètres et le graphe ne sont pas à jours...";
            }
        }
    });
}
setTextAJour();