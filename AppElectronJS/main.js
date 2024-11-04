const { app, BrowserWindow, ipcMain, Menu ,nativeTheme } = require('electron')
const path = require('node:path');
const { spawn } = require('child_process');
const fs = require("fs");


let mainWindow;

const webPref = {
  preload: path.join(__dirname, 'preload.js'),  // Chemin vers votre script de preload
  contextIsolation: true,  // Active l'isolation de contexte pour la sécurité
  enableRemoteModule: false, // Désactive le module remote par sécurité
  nodeIntegration: true, // Active Node.js dans le script de preload
  sandbox: false  // Ajoutez sandbox: false pour éviter des problèmes de compatibilité
}

const isDev = process.env.NODE_ENV !== 'production';
const isMac = process.platform === 'darwin';

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: isDev ? 1000 : 500,
    height: 600,
    icon: path.join(__dirname, 'renderer/images/logoWindow.png'),
    webPreferences: webPref,
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.loadFile('renderer/loadcsv.html');

  const mainMenu = Menu.buildFromTemplate(mainMenuTemplates)
  Menu.setApplicationMenu(mainMenu)
}

// Fonction pour exécuter le script Python
function runPythonFunction(params) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ["-m", 'Bokeh.src.mainPyvis', ...params]);
        console.log(...params);
        let output = '';
        pythonProcess.stdout.on('data', (data) => {
            data += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            reject(data.toString());
        });

        pythonProcess.on('close', (code) => {
          if (code === 0) {
            resolve(output); // Processus terminé avec succès
          } else {
            reject(`Processus terminé avec un code d'erreur : ${code}`);
          }
        });
    });
}



ipcMain.handle('callFunctionSearch', (event, query) => {
  // Appel de la fonction Python avec les paramètres fournis
  return runPythonFunction(query)
      .then((output) => {
          // Une fois le processus Python terminé, charger la nouvelle page HTML
          mainWindow.loadFile('renderer/test.html'); 
          return output;  // Renvoyer la sortie du script Python
      })
      .catch((error) => {
          // En cas d'erreur, renvoyer l'erreur
          return `Error: ${error}`;
      });
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
      }
    ]
  },
  {
    label:'Settings',
    submenu:[
      {
        // Switch entre Dark mode et Light mode
        label:'Switch Dark Mode',
        accelerator: process.platform == 'darwin' ? 'Command+M' : 'Ctrl+M',
        click(){

          // Looking for actual theme
          if (nativeTheme.shouldUseDarkColors) {
            nativeTheme.themeSource = 'light';
        } else {
            nativeTheme.themeSource = 'dark';
        }

        return nativeTheme.shouldUseDarkColors;
        }
      },
      {
        label: 'Gerer les couleurs',
        // accelerator: process.platform == 'darwin' ? 'Command+C' : 'Ctrl+C',
        click(){
          // Une fenêtre pour gerer les couleurs des noeuds 
          const fenetre = new BrowserWindow({
            width: 800,
            height: 600,
            icon: path.join(__dirname, 'renderer/images/logoWindow.png'),
            webPreferences: webPref
        });
        fenetre.loadFile('./renderer/colorSettings.html');
        }
      }
    ]
  }
];


// For mac user
if (process.platform == 'darwin'){
  mainMenuTemplates.unshift({});
}

// For product environement, add devTool menu and accelerator
if (isDev){
  mainMenuTemplates.push({
    label:'Developer Tools',
    submenu:[
      {
        label:'Toggle devTools',
        accelerator: process.platform == 'darwin' ? 'Command+I' : 'Ctrl+I',
        click(item, focusedWindow){
          focusedWindow.toggleDevTools();
        }
      },
      {
        role:'reload'
      }
    ]
  });
}

ipcMain.on('load-search-page', () => {
  mainWindow.loadFile('renderer/search.html');
});

