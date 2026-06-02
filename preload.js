const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
  start: (date, config) => ipcRenderer.send("start", date, config),
});