const { app, BrowserWindow, ipcMain, Menu ,nativeTheme, dialog } = require('electron')
const path = require('node:path');
const { spawn, exec } = require('child_process');
const fs = require("fs");


let mainWindow;
let graphWindo;

const webPref = {
  preload: path.join(__dirname, 'preload.js'),  // Chemin vers votre script de preload
  contextIsolation: true,  // Active l'isolation de contexte pour la sécurité
  enableRemoteModule: false, // Désactive le module remote par sécurité
  nodeIntegration: true, // Active Node.js dans le script de preload
  sandbox: false  // Ajoutez sandbox: false pour éviter des problèmes de compatibilité
}

const isDev = process.env.NODE_ENV !== 'production';
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
    const data = await fs.promises.readFile('./renderer/json/userSettings.json', 'utf-8');
    const parsedData = JSON.parse(data); // Analyse JSON

    // Vérifie si le chemin CSV existe dans le JSON
    const pathCSV = parsedData.CSVChoose;
    
    if (pathCSV && fs.existsSync(`${parsedData.pathDirectoryCSV}/${parsedData.CSVChoose}`)) {
        mainWindow.loadFile('renderer/search.html');
    } else {
        mainWindow.loadFile('renderer/loadcsv.html');
    }
} catch (error) {
    console.error("Erreur de lecture ou d'analyse du fichier JSON :", error);
    mainWindow.loadFile('renderer/loadcsv.html'); // En cas d'erreur, charge une page de secours
}



  const mainMenu = Menu.buildFromTemplate(mainMenuTemplates)
  Menu.setApplicationMenu(mainMenu)
}

// Fonction pour exécuter le script Python
function runPythonFunction(params) {
    err = new Promise((resolve, reject) => {
      const pythonProcess = spawn('python', ["-m", 'Bokeh.src.mainPyvis', ...params]);
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
  graphWindo.loadFile('./renderer/test.html');
}

ipcMain.handle('callFunctionSearch', (event, query, specialEvent = false) => {

  if(query.length == 3 && query[2]){
    
    runPythonFunction(query).then( () => {openOtherWindow();});
    
  }else{

    // Appel de la fonction Python avec les paramètres fournis
    return runPythonFunction(query)
    .then((output) => {
        // Une fois le processus Python terminé, charger la nouvelle page HTML
        mainWindow.loadFile('renderer/test.html'); 
        return output;  // Renvoyer la sortie du script Python
    })
    .catch((error) => {
        // En cas d'erreur, renvoyer l'erreur
        // !!! ne pas changer le texte Error en dessous, important pour la gestion d'erreur dans renderer.js
        return `Error: ${error}`;
    });
  }
});

app.whenReady().then(() => {
  createWindow();
  
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
    submenu:[
      {
        label:'Quit',
        accelerator: process.platform == 'darwin' ? 'Command+Q' : 'Ctrl+Q',
        click(){
          app.quit();
        }
      },
      {
        label:'Open other CSV',
        click(){
          mainWindow.loadFile('./renderer/loadcsv.html'); 
        }
      }
    ]
  },
  {
    label:'Settings',
    submenu:[
      {
        label: 'Gerer les couleurs',
        // accelerator: process.platform == 'darwin' ? 'Command+C' : 'Ctrl+C',
        click(){
          // Une fenêtre pour gerer les couleurs des noeuds 
          graphWindo = new BrowserWindow({
            width: 800,
            height: 600,
            icon: path.join(__dirname, 'renderer/images/logoWindow.png'),
            webPreferences: webPref
        });
        graphWindo.loadFile('./renderer/test.html');
        }
      }
    ]
  }
];


ipcMain.handle('openWindoColor', (event) => {
    const fenetre = new BrowserWindow({
      width: 800,
      height: 600,
      icon: path.join(__dirname, 'renderer/images/logoWindow.png'),
      webPreferences: webPref
  });
  fenetre.loadFile('./renderer/colorSettings.html');
});

ipcMain.handle("reloadPage", (event) => {

  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.reloadIgnoringCache();
  } else {
    console.error("La fenêtre mainWindow n'est pas définie ou n'a pas de webContents");
  }
  
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
  mainWindow.loadFile('renderer/loading.html');

  // Exécute le script Python
  exec('python recup_data.py', (error, stdout, stderr) => {
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
      mainWindow.loadFile('renderer/search.html');
  });
});

ipcMain.on('send-csv-path', (event, csvPath) => {
  console.log(`Chemin du CSV reçu : ${csvPath}`);

  // Appeler le script Python avec le chemin en paramètre
  const command = `python recup_data.py ${csvPath}`;
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

