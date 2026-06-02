const { app, BrowserWindow, ipcMain, powerSaveBlocker } = require("electron");
const path = require("path");

const createAppWindow = () => {
  const win = new BrowserWindow({
    width: 360,
    height: 500,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  win.setAutoHideMenuBar(true);
  win.setMenuBarVisibility(false);

  win.loadFile("index.html");
};

const createCafeWindow = (date, config) => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "inject.js"),
      nodeIntegration: true,
      webSecurity: false,
    },
  });

  win.setAutoHideMenuBar(true);
  win.setMenuBarVisibility(false);
  win.loadURL("https://museum-tickets.nintendo.com/en/calendar");

  win.webContents.on("did-finish-load", () => {
    // 将配置对象转换为 JSON 字符串传递
    const configJson = JSON.stringify(config);
    win.webContents.executeJavaScript(
      `window.electron.inject("${date}", ${configJson});`
    );
  });

  const lock = powerSaveBlocker.start("prevent-display-sleep");
  win.on("close", () => {
    powerSaveBlocker.stop(lock);
  });
};

app.whenReady().then(() => {
  createAppWindow();
});

ipcMain.on("start", (_, date, config) => {
  createCafeWindow(date, config);
});