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

  mainWindow.loadFile('renderer/index.html');
}

// Fonction pour exécuter le script Python
function runPythonFunction(params) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('python', ["-m", 'Bokeh.src.mainPyvis', ...params]);
        console.log(params);
        pythonProcess.stdout.on('data', (data) => {
            resolve(data.toString());
        });

        pythonProcess.stderr.on('data', (data) => {
            reject(data.toString());
        });
    });
}

// Gestionnaire IPC pour la recherche
ipcMain.handle('callFunctionSearch', async (event, query) => {
    try {
        const output = await runPythonFunction([query]); // Le paramètre est la requête de recherche

        // Une fois la fonction Python terminée, on charge la nouvelle page HTML
        
        mainWindow.loadFile('Bokeh/bin/nx.html'); // Charger une nouve
        return output;
    } catch (error) {
    
        return `Error: ${error}`;
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

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit(); 
  }
});
