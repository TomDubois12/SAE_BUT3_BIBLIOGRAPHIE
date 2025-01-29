


function writeWordChoose(newWord){
    window.api.readFile('renderer/json/userSettings.json', (err, data) => {
        if (data) {
            // On récupère le fichier
            data = JSON.parse(data);

            // On prend le mot actuel et le remplace par le nouveau 
            data.WordChoose = newWord

            // On sauvegarde les modification
            window.api.writeFile('renderer/json/userSettings.json',JSON.stringify(data), (err) => {  
            console.error('Erreur d’écriture :', err);
            });

        }
    });
};

