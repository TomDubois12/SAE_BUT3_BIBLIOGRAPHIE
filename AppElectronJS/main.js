const { app, BrowserWindow, ipcMain } = require('electron/main')
const path = require('node:path')


const isDev = process.env.NODE_ENv !== 'production';
const isMac = process.platfrom === 'darwin';
const createWindow = () => {
  const win = new BrowserWindow({
    width: isDev ? 1000 : 500,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  })

  if (isDev) {
    win.webContents.openDevTools();
  }

  win.loadFile('./renderer/index.html')
}

app.whenReady().then(() => {
  ipcMain.handle('ping', () => 'pong')
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})