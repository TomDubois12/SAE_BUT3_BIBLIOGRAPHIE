const fs = require("fs");
const { contextBridge, ipcRenderer, dialog } = require('electron');

let queue = Promise.resolve();

// Fonction pour ajouter une tâche dans la file d'attente
function addToQueue(task, callback) {
    queue = queue
      .then(task)
      .then((result) => callback(null, result)) // Envoie le résultat au callback en cas de succès
      .catch((err) => callback(err)); // Envoie l'erreur au callback en cas d'échec
  }

// Lire un fichier (ajouté à la file d'attente)
function readFile(path, callback) {
    addToQueue(() => {
      return new Promise((resolve, reject) => {
        fs.readFile(path, 'utf-8', (err, data) => {
          if (err) return reject(err);
          resolve(data);
        });
      });
    }, callback);
  }
// Écrire dans un fichier (ajouté à la file d'attente)
function writeFile(path, data, callback) {
    addToQueue(() => {
      return new Promise((resolve, reject) => {
        fs.writeFile(path, data, (err) => {
          if (err) return reject(err);
          resolve();
        });
      });
    }, callback);
  }

contextBridge.exposeInMainWorld('api', { 
    callFunctionSearch: async (query) => {
        return await ipcRenderer.invoke('callFunctionSearch', query);
    },
    openWindoColor: async () => {
        return await ipcRenderer.invoke('openWindoColor');
    },
    readFile: (path, callback) => fs.readFile(path, 'utf-8', callback), // readFile(path, callback), fs.readFile(path, 'utf-8', callback),
    writeFile: (path, data, callback) => writeFile(path, data, callback), //fs.writeFile(path, data, callback),
    reloadGraph: async () => {
        return await ipcRenderer.invoke('reloadPage');
    },

    accesLoadCSV: () => ipcRenderer.invoke('loadCSVpage')

});


contextBridge.exposeInMainWorld('electronAPI', {
    accessBiblioLectio: () => ipcRenderer.send('load-search-page'),
    
    saveCSVPath: async (file) => {
        try {
            // Lire les paramètres d'utilisateur
            const settingFileData = await fs.promises.readFile("./renderer/json/userSettings.json", 'utf-8');
            const settings = JSON.parse(settingFileData);
            const pathDirectory = settings.pathDirectoryCSV;

            // Vérifier si le fichier existe déjà
            const filePath = `${pathDirectory}/${file.name}`;
            if (!fs.existsSync(filePath)) {
                // Lancer la lecture du fichier
                const reader = new FileReader();
                
                reader.onload = async (event) => {
                    const content = event.target.result;
                    console.log(content); // Affiche le contenu du fichier CSV

                    // Écriture du fichier
                    try {
                        await fs.promises.writeFile(filePath, content, 'utf8');
                        console.log("Fichier CSV créé avec succès !");
                        settings.CSVChoose = file.name;

                        // Mettre à jour userSettings.json
                        await fs.promises.writeFile("./renderer/json/userSettings.json", JSON.stringify(settings));
                    } catch (writeErr) {
                        console.error("Erreur lors de la création du fichier CSV :", writeErr);
                    }
                };

                // Lire le fichier comme texte (vous devez avoir accès à l'objet file)
                reader.readAsText(file); // Assurez-vous que `file` est un objet `File`
            } else {
                console.log("Le fichier CSV existe déjà.");
                settings.CSVChoose = file.name;

                // Mettre à jour userSettings.json
                await fs.promises.writeFile("./renderer/json/userSettings.json", JSON.stringify(settings));
            }
        } catch (error) {
            console.error("Erreur lors de la lecture ou de l'écriture du fichier :", error);
        }
    },

    on: (event, callback) => {
        ipcRenderer.on(event, (event, ...args) => callback(...args)); // Permet d'écouter des événements
    },

    sendCSVPath: (csvFilePath) => ipcRenderer.send('load-search-page', csvFilePath),
    addArticle: (newArticle) => ipcRenderer.send('add-article', newArticle),
    suggestions: (nb_citations) => ipcRenderer.invoke('suggestions', nb_citations),


});



