const fs = require("fs");
const { contextBridge, ipcRenderer } = require('electron');


contextBridge.exposeInMainWorld('api', { 
    callFunctionSearch: async (query) => {
        return await ipcRenderer.invoke('callFunctionSearch', query);
    },
    
    readFile: (path, callback) => fs.readFile(path, 'utf-8', callback),
    writeFile: (path, data, callback) => fs.writeFile(path, data, callback),
});


  