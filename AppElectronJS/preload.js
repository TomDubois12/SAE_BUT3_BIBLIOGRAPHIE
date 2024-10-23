const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
    callFunctionSearch: async (query) => {
        return await ipcRenderer.invoke('callFunctionSearch', query);  // Notez 'callFunctionSearch'
    }
});
