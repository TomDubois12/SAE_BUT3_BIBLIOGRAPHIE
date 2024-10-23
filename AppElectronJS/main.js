const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const { spawn } = require('child_process');

let mainWindow;

const isDev = process.env.NODE_ENV !== 'production';
const isMac = process.platform === 'darwin';

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: isDev ? 1000 : 500,
    height: 600,
    webPreferences: {
        nodeIntegration: false,
        contextIsolation: true, // Important pour la sécurité
        preload: path.join(__dirname, 'preload.js')
    }
  });

  if (isDev) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.loadFile('Bokeh/template/search.html');
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
          mainWindow.loadFile('Bokeh/bin/nx.html'); 
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

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit(); 
  }
});
