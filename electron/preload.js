const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('monthlyStar', {
  getState: () => ipcRenderer.invoke('app:get-state'),
  chooseDirectory: (currentPath) => ipcRenderer.invoke('app:choose-directory', currentPath),
  openPath: (targetPath) => ipcRenderer.invoke('app:open-path', targetPath),
  startGeneration: (options) => ipcRenderer.invoke('app:start-generation', options),
  onLog: (callback) => ipcRenderer.on('generation-log', (_event, payload) => callback(payload)),
  onFinished: (callback) => ipcRenderer.on('generation-finished', (_event, payload) => callback(payload)),
});
