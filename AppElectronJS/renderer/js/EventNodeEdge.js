async function changeColorOnHover(nodeId, isOrigin) {

    // Obtenir la couleur associée au nœud (origine ou non)
    const color = await getColorParamUser(isOrigin);
    console.log(color,isOrigin);

    // Appliquer la couleur au nœud immédiatement
    network.body.data.nodes.update({
        id: nodeId,
        color: color,
        borderWidth: 3,
        shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 10, x: 5, y: 5 },
    });

    // Si vous voulez vraiment que la couleur revienne après un certain délai, il faut 
    // vous assurer que la couleur reste avant le retour à la couleur d'origine.

}
async function changeBlurColor(nodeId, isOrigin){
    // Obtenir la couleur associée au nœud (origine ou non)
    const color = await getColorParamUser(isOrigin);
    console.log(color,isOrigin);

    network.body.data.nodes.update({
        id: nodeId,
        color: color,
        borderWidth: 0,
       shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 10, x: 5, y: 5 },
    });
    // Délai avant de remettre la couleur d'origine (si nécessaire)
}




function changeColorOnClick(nodeId){
    //console.log(network.body.data.nodes.get("10.1023/A:1004761103919"));
    network.body.data.nodes.update({
        id: nodeId,
        color: { 
            background: '#ffffff', 
            border: 'black', 
            highlight: { background: 'yellow', border: 'black' } 
        },
        borderWidth: 3,
        shadow: { enabled: true, color: 'rgba(0,0,0,0.5)', size: 10, x: 5, y: 5 },
    });
}

function createAside(nodeId){

    if (!nodeId){return null;}
    const canva = document.getElementsByClassName('contenerCanvaAside')[0]; // Accès au premier élément
    const className = 'generated-div';
    
    // Retrieve the title from the node attributes
    
    const nodeData = network.body.data.nodes.get(nodeId); // Utiliser un autre nom pour éviter la confusion

    // Check for existing aside element by ID
    const existingIdenticalElement = document.getElementById(nodeId);
        
    // If the existing aside is found, remove it
    if (existingIdenticalElement) {
        existingIdenticalElement.remove();
    } else {
        const existingElements = document.getElementsByClassName(className);
        // Remove the first existing element if it exists
        if (existingElements.length > 0) {existingElements[0].remove();}
        if (!nodeId) {try {existingElements[0].remove();}catch{console.log("cc")}}

        // Create a new aside element
        const aside = document.createElement("aside");

        // Add content to the aside, including the title
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
        
        const doi = document.createElement("a");
        doi.classList.add("pDOI");
        doi.textContent = `DOI : ${nodeData.doi || "DOI non disponible"}`;
        doi.href = nodeData.citations || "#";  // Set the URL for the link, default to "#" if DOI not available
        doi.target = "_blank";  // Open the link in a new tab
        doi.rel = "noopener noreferrer";  // Security measure to prevent exploitation
        aside.appendChild(doi);

        aside.classList.add(className); // Add class for styling
        aside.id = nodeId; // Assign unique ID

        // Append the aside to the DOM
        canva.appendChild(aside);
        //console.log(`Un nouvel aside a été créé pour ${nodeId} avec le titre "${nodeData.title || "Titre non disponible"}" publié en "${nodeData.year || "Année non disponible"}".`);
    }
}



function onClick(params) {
    
    // On prend la nodeId en fonction de si c'est un click ou un hover
    const nodeId = params.nodes[0];
    if (!nodeId) {return null;}
    
    // En premier lieu on creer l'aside
    createAside(nodeId);
    changeColorOnClick(nodeId)
    
    // if (params.nodes > 0) {
    //     console.log("Clicked node:", nodeId);
    //     // Here you can add more functionality, like fetching data
    // }
}

function onHover(params){
    const nodeId = params.node;
    createAside(nodeId)
    changeColorOnHover(nodeId,network.body.data.nodes.get(nodeId).isOrigin);
}

function onBLur(params){
    const nodeId = params.node;
    changeBlurColor(nodeId,network.body.data.nodes.get(nodeId).isOrigin);
}

function getColorParamUser(isOrigin) {
    // Créer une promesse pour gérer l'asynchronicité
    console.log(isOrigin);
    return new Promise((resolve, reject) => {
        window.api.readFile('renderer/json/userSettings.json', (err, data) => {
            if (err) {
                reject('Erreur lors de la lecture du fichier');
            } else if (data) {
                data = JSON.parse(data);
                // Parcourir les éléments et retourner la couleur appropriée
                var colorToReturn = "#000000";
                data.ListeNoeudSettings.forEach(element => {
                    if (isOrigin && element.NoeudsName === "Nombre de nodes à l'origine ") {
                        colorToReturn = element.color;  // Résoudre la promesse avec la couleur de l'origine
                    } else {
                        colorToReturn = element.color;  // Résoudre la promesse avec la couleur des autres noeuds
                    }
                });
                resolve(colorToReturn)
            } else {
                resolve("#000000");  // Retourner une couleur par défaut si les données sont vides
            }
        });
    });
}


network.on("click", onClick);
network.on("hoverNode", onHover);
network.on("blurNode", onBLur);