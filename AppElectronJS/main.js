const { app, BrowserWindow, ipcMain, Menu ,nativeTheme, dialog, Notification,globalShortcut  } = require('electron')
const path = require('node:path');
const { spawn, exec, spawnSync } = require('child_process');
const fs = require("fs");
const { stdout, stderr } = require('node:process');

const isDev = process.env.NODE_ENV !== 'production';
const logFilePath = path.join(__dirname, 'app.log');


let pythonExecutable;

let mainWindow;
let graphWindo;

if (process.platform === 'win32') {
    pythonExecutable = path.join(__dirname, 'python', 'python-portable', 'python.exe');
} else {
    pythonExecutable = path.join(__dirname, '../../venv', 'bin', 'python');
}

// Fonction utilitaire pour écrire dans le fichier de log
function writeToLogFile(message) {
  const formattedMessage = `[${new Date().toISOString()}] ${message}\n`;
  fs.appendFileSync(logFilePath, formattedMessage, 'utf8'); // Écriture dans le fichier log
}

// Redéfinir console.error
console.error = (...args) => {
  const message = args.join(' ');
  writeToLogFile(`ERROR: ${message}`);
  process.stderr.write(`${message}\n`); // Affiche aussi dans la console
};

// Redéfinir console.log
console.log = (...args) => {
  const message = args.join(' ');
  writeToLogFile(`LOG: ${message}`);
  process.stdout.write(`${message}\n`); // Affiche aussi dans la console
};


function installPythonDependencies() {
  // Vérifie que l'exécutable Python existe dans le virtualenv
  if (!fs.existsSync(pythonExecutable)) {
      console.error('Python executable not found in virtualenv:', pythonExecutable);
      return;
  }
}

const webPref = {
  preload: path.join(__dirname, 'preload.js'),  // Chemin vers votre script de preload
  contextIsolation: true,  // Active l'isolation de contexte pour la sécurité
  enableRemoteModule: false, // Désactive le module remote par sécurité
  nodeIntegration: true, // Active Node.js dans le script de preload
  sandbox: false  // Ajoutez sandbox: false pour éviter des problèmes de compatibilité
}

//const isDev = process.env.NODE_ENV !== 'production';
const isMac = process.platform === 'darwin';

const createWindow = async () => {
  mainWindow = new BrowserWindow({
    width: isDev ? 1000 : 500,
    height: 600,
    icon: path.join(__dirname, 'renderer/images/logoWindow.png'),
    webPreferences: webPref,
  });

  if (isDev) {
    // mainWindow.webContents.openDevTools();
  }

  try {
    // Utilisation de fs.promises.readFile pour lire le fichier de manière asynchrone
    const data = await fs.promises.readFile(path.join(__dirname, 'renderer/json/userSettings.json'), 'utf-8');
    const parsedData = JSON.parse(data); // Analyse JSON

    // Vérifie si le chemin CSV existe dans le JSON
    const pathCSV = parsedData.CSVChoose;
    console.log(`${parsedData.pathDirectoryCSV}/${parsedData.CSVChoose}`);
    console.log(path.join(__dirname,`${parsedData.pathDirectoryCSV}/${parsedData.CSVChoose}`));

    if (pathCSV && fs.existsSync(path.join(__dirname,`${parsedData.pathDirectoryCSV}/${parsedData.CSVChoose}`))) {
        mainWindow.loadFile(path.join(__dirname,'renderer/accueil.html'));
    } else {
        mainWindow.loadFile(path.join(__dirname, 'renderer/loadcsv.html'));
    }
} catch (error) {
    console.error("Erreur de lecture ou d'analyse du fichier JSON :", error);
    mainWindow.loadFile(path.join(__dirname, 'renderer/loadcsv.html')); // En cas d'erreur, charge une page de secours
}



  const mainMenu = Menu.buildFromTemplate(mainMenuTemplates)
  Menu.setApplicationMenu(mainMenu)
}

// Fonction pour exécuter le script Python
function runPythonFunction(params) {
    err = new Promise((resolve, reject) => {
      const pythonProcess = spawn(pythonExecutable, [path.join(__dirname, 'Pyvis/src/mainPyvis.py') , ...params]);
      console.log(...params);
      let output = '';

      //Cette fonction récupère les sortie du terminal, pour vérifier si une erreur est apparue je met toute la sortie en forme de 
      //liste de ligne puis je regarde l'avant dernière ligne ou est sensé se trouver une erreur et si oui alors je la traite.
      pythonProcess.stdout.on('data', (data) => {
          data += data.toString();
          data = data.split("\n");
          if(data[data.length-2].split(" : ")[1] == 1001){
            dialog.showMessageBox({
              type: 'warning',
              title: 'Mot clé vide',
              message: "Il semblerait qu'il n'y ait pas de mot clé saisies ?",
            });
            reject("Processus terminé avec un code d'erreur");
          }
          if(data[data.length-2].split(" : ")[1] == 1002){
            dialog.showMessageBox({
              type: 'warning',
              title: 'Aucun résultat',
              message: "La recherche effectuée ne renvoie aucun résultat.",
            });
            reject("Processus terminé avec un code d'erreur");
          }
          if(data[data.length-2].split(" : ")[1] == 1003){
            dialog.showMessageBox({
              type: 'warning',
              title: 'Mauvais DOI',
              message: "Le DOI entrer ne figure pas dans vos données.",
            });
            reject("Processus terminé avec un code d'erreur");
          }
      });



      pythonProcess.stderr.on('data', (data) => {
          reject(data.toString());
          console.error(`Python stderr: ${data}`);
      }); 

      pythonProcess.on('close', (code) => {
        if (code === 0) {

          resolve(output); // Processus terminé avec succès
        } else {
          dialog.showMessageBox({
            type: 'error',
            title: 'Erreur',
            message: "Une erreur est survenue : Vérifier que vous avez entrez un mot de recherche ",
          });
          reject(`Processus terminé avec un code d'erreur : ${code}`);
        }
      });
  });

    

  return err;
}

function openOtherWindow(){
  graphWindo = new BrowserWindow({
    width: isDev ? 1000: 500,
    height: 600,
    icon: path.join(__dirname, 'renderer/images/logoWindow.png'),
    webPreferences: webPref
  });
  graphWindo.loadFile(path.join(__dirname, 'renderer/graphe.html'));
}

ipcMain.handle('callFunctionSearch', (event, query) => {

  if(query.length == 3 && query[2]){
    
    runPythonFunction(query).then( () => {openOtherWindow();});
    
  }else{

    // Appel de la fonction Python avec les paramètres fournis
    return runPythonFunction(query)
    .then((output) => {
        // Une fois le processus Python terminé, charger la nouvelle page HTML
        mainWindow.loadFile(path.join(__dirname, 'renderer/graphe.html')); 
        return output;  // Renvoyer la sortie du script Python
    })
    .catch((error) => {
        // En cas d'erreur, renvoyer l'erreur
        // !!! ne pas changer le texte Error en dessous, important pour la gestion d'erreur dans renderer.js
        return `Error: ${error}`;
    });
  }
});

function showNotification() {
  new Notification({
    title: 'Notification Electron',
    body: 'Votre application Electron est prête !'
  }).show();
}

app.whenReady().then(() => {
  // Vérifiez si les dépendances doivent être installées
  installPythonDependencies();
  
  showNotification();
  createWindow();
    globalShortcut.register('CommandOrControl+F', () => {
      mainWindow.webContents.send('trigger-search');
  });
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

//For mac users, close app 
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit(); 
  }
});

// Change the global menu
const mainMenuTemplates = [
  {
      label: 'File',
      submenu: [
          {
              label: 'Quit',
              accelerator: process.platform === 'darwin' ? 'Command+Q' : 'Ctrl+Q',
              click() {
                  app.quit();
              },
          },
          {
              label: 'Open other CSV',
              click() {
                  mainWindow.loadFile(path.join(__dirname, './renderer/loadcsv.html'));
              },
          },
          {
            label: 'Remplacer le cache DOI',
            click() {
                replaceCacheFile();
            },
          }
      ],
    },
  {
    label:'Settings',
    submenu:[
      {
        label:'Ajouter un article',
        click(){
          mainWindow.loadFile(path.join(__dirname, './renderer/ajout_article.html')); 
        }
      }
    ]
  }
];
function replaceCacheFile() {
  const filePath = path.join(__dirname, 'cache_doi.json'); // Emplacement du cache actuel

  // Ouvre une boîte de sélection pour choisir un fichier
  const files = dialog.showOpenDialogSync({
      title: 'Sélectionnez un fichier JSON pour remplacer le cache DOI',
      filters: [{ name: 'JSON Files', extensions: ['json'] }], // Seuls les fichiers JSON sont affichés
      properties: ['openFile'],
  });

  if (!files || files.length === 0) {
      // Si l'utilisateur annule la sélection
      dialog.showMessageBoxSync({
          type: 'info',
          title: 'Action annulée',
          message: 'Aucun fichier n’a été sélectionné.',
      });
      return;
  }

  const selectedFile = files[0]; // Le fichier sélectionné

  try {
      // Lire le contenu du fichier sélectionné
      const fileContent = fs.readFileSync(selectedFile, 'utf8');

      // Vérifie si le fichier est un JSON valide
      JSON.parse(fileContent);

      // Remplace le fichier cache actuel
      fs.writeFileSync(filePath, fileContent, 'utf8');

      dialog.showMessageBoxSync({
          type: 'info',
          title: 'Succès',
          message: `Le fichier ${selectedFile} a remplacé le cache DOI avec succès.`,
      });
  } catch (error) {
      // Gérer les erreurs, par exemple si le fichier n'est pas un JSON valide
      dialog.showMessageBoxSync({
          type: 'error',
          title: 'Erreur',
          message: 'Le fichier sélectionné n’est pas un JSON valide ou une erreur est survenue.',
      });
  }
}

ipcMain.handle('openWindoColor', (event) => {
    const fenetre = new BrowserWindow({
      width: 800,
      height: 600,
      icon: path.join(__dirname, 'renderer/images/logoWindow.png'),
      webPreferences: webPref
  });
  fenetre.loadFile(path.join(__dirname, './renderer/colorSettings.html'));
});

ipcMain.handle("reloadPage", (event) => {

  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.reloadIgnoringCache();
  } else {
    console.error("La fenêtre mainWindow n'est pas définie ou n'a pas de webContents");
  }
  
});

ipcMain.handle("loadCSVpage", (event) => {
  mainWindow.loadFile(path.join(__dirname, './renderer/loadcsv.html')); 
});

// For mac user
if (process.platform == 'darwin'){
  mainMenuTemplates.unshift({}); 
}

// For product environement, add devTool menu and accelerator
if (isDev){
  mainMenuTemplates.push({
    label:'Developer Tools', // Ajout d'un menu si le dev ce connecte
    submenu:[
      {
        label:'Toggle devTools',
        accelerator: process.platform == 'darwin' ? 'Command+I' : 'Ctrl+I', // Différencier l'environnement mac des autres 
        click(item, focusedWindow){
          focusedWindow.toggleDevTools();
        }
      },
      {
        role:'reload'  // permet de refresh l'app
      }
    ]
  });
}

ipcMain.on('load-search-page', (event) => {
  // Charge immédiatement la page de chargement
  mainWindow.loadFile(path.join(__dirname, 'renderer/loading.html'));

  // Exécute le script Python
  exec(pythonExecutable + ' '+path.join(__dirname, 'recup_data.py'), (error, stdout, stderr) => {
      if (error) {
          console.error(`Erreur d'exécution: ${error.message}`);
          event.sender.send('python-error', error.message);
          return;
      }
      if (stderr) {
          console.error(`stderr: ${stderr}`);
          event.sender.send('python-error', stderr);
          return;
      }
      console.log(`stdout: ${stdout}`);

      // Redirige vers la page finale après l'exécution
      mainWindow.loadFile(path.join(__dirname, 'renderer/accueil.html'));
  });
});
ipcMain.on('save-articles', (event) => {
  // On crée le fichier s'il n'existe pas
  fs.writeFile(path.join(__dirname, "Data/AllSavedDOI.csv"), '', (err) => {
    if (err) {
      console.error('Erreur lors de la lecture du fichier:', err);
      return;
    }
  });

  // Lire le fichier cache_doi 
  fs.readFile(path.join(__dirname, "cache_doi.json"), 'utf-8', (err, data) => {
    if (err) {
      console.error('Erreur lors de la lecture du fichier:', err);
      return;
    }
  
    try {
      const jsonData = JSON.parse(data);  // Convertir en objet JSON
      let csvContent = "DOI\n";  // En-tête du fichier CSV

      // Ajouter chaque clé comme ligne dans le CSV
      Object.keys(jsonData).forEach(key => {
        csvContent += `${key}\n`;
      });

      fs.writeFile(path.join(__dirname, "Data/AllSavedDOI.csv"), csvContent, (err) => {
        if (err) {
          console.error('Erreur lors de l\'écriture du fichier:', err);
          return;
        }
        console.log(csvContent);
        console.log("Cache lu et sauvegardé dans AllSavedDOI.csv")
      });

    } catch (parseError) {
      console.error('Erreur de parsing JSON:', parseError);
    }
  });

  // Lire et modifier userSettings.json
  fs.readFile(path.join(__dirname, "renderer/json/userSettings.json"), 'utf-8', (err, settingFileData) => {
    if (err) {
      console.error("Erreur lors de la lecture du fichier :", err);
      return;
    }

    try {
      const settings = JSON.parse(settingFileData);
      settings.CSVChoose = "AllSavedDOI.csv";

      fs.writeFile(path.join(__dirname, "renderer/json/userSettings.json"), JSON.stringify(settings, null, 2), 'utf-8', (err) => {
        if (err) {
          console.error("Erreur lors de l'écriture du fichier :", err);
        } else {
          console.log("Fichier de paramètres mis à jour avec succès.");
        }

        // 🔹 🔥 NOTIFIER QUE TOUT EST FINI 🔥 🔹
        event.reply('save-articles-done');
      });

    } catch (error) {
      console.error("Erreur lors du traitement des fichiers :", error);
    }
  });
});



ipcMain.on('send-csv-path', (event, csvPath) => {
  console.log(`Chemin du CSV reçu : ${csvPath}`);

  // Appeler le script Python avec le chemin en paramètre
  const command = pythonExecutable + ' '+path.join(__dirname, `recup_data.py ${csvPath}`);
  exec(command, (error, stdout, stderr) => {
      if (error) {
          console.error(`Erreur lors de l'exécution du script Python : ${error.message}`);
          return;
      }
      if (stderr) {
          console.error(`Erreur standard : ${stderr}`);
          return;
      }
      console.log(`Sortie du script Python : ${stdout}`);
  });
});

ipcMain.on('add-article', (event, newArticle) => {
  console.log(`Nouveau article: ${newArticle}`);
  
  // Ligne a changé pour adapter au __dirname

  const command = pythonExecutable + ' ' + path.join(__dirname, `recup_data.py ajout_article ${newArticle}`);
  //const command = pythonExecutable + ` -c "from recup_data import ajout_article; ajout_article('${newArticle}')"`;

  exec(command, { maxBuffer: 4096 * 4096  },(error, stdout, stderr) => {
    if (error) {
        console.error(`Erreur lors de l'exécution du script Python : ${error.message}`);
        event.reply('article-response', 'Impossible d\'ajouter l\'article');
        return;
    }
    if (stderr) {
        console.error(`Erreur standard : ${stderr}`);
        event.reply('article-response', 'Impossible d\'ajouter l\'article');
        return;
    }

    // Si stdout est 'None' ou vide
    if (!stdout || stdout.trim() === "None") {
        event.reply('article-response', 'Impossible d\'ajouter l\'article');
    } else {
        event.reply('article-response', 'Article ajouté avec succès');
    }

    console.log(`Sortie du script Python : ${stdout}`);
  });
});

ipcMain.handle('suggestions', async (event, nb_citations) => {
  console.log(`Recherche avec: ${nb_citations}`);

  const command = pythonExecutable + ' ' + path.join(__dirname, `recup_data.py get_suggestions ${nb_citations}`);
  //const command = `python -c "from recup_data import get_suggestions; print(get_suggestions('${nb_citations}'))"`;

  return new Promise((resolve, reject) => {
    exec(command,{ maxBuffer: 4096 * 4096  }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Erreur lors de l'exécution du script Python : ${error.message}`);
        reject('Impossible d\'ajouter l\'article');
        return;
      }
      if (stderr) {
        console.error(`Erreur standard : ${stderr}`);
        reject('Impossible d\'ajouter l\'article');
        return;
      }
    
      // Vérification de la sortie brute
      console.log('Sortie brute:', stdout);
    
      // Nettoyer les espaces, les nouvelles lignes et les caractères invisibles
      const cleanedStdout = stdout.replace(/[\u200B-\u200D\uFEFF]/g, '')  // Supprimer les caractères invisibles
                                   .replace(/[\r\n]+/g, '');  // Supprimer les retours à la ligne supplémentaires
    
      console.log('Sortie nettoyée:', cleanedStdout);
    
      // Vérification de la validité du JSON
      try {
        const suggestions = JSON.parse(cleanedStdout);
        resolve(JSON.stringify(suggestions, null, 2));
      } catch (parseError) {
        console.error('Erreur lors de l\'analyse JSON:', parseError);
        console.error('Contenu nettoyé de stdout:', cleanedStdout);  // Afficher stdout nettoyé pour le débogage
        reject('Impossible de traiter les suggestions.');
      }
    });
    

  });
});

