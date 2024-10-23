const { app, BrowserWindow, ipcMain, Menu ,nativeTheme } = require('electron')
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

  mainWindow.loadFile('renderer/search.html');

  const mainMenu = Menu.buildFromTemplate(mainMenuTemplates)
  Menu.setApplicationMenu(mainMenu)
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