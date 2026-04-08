const { app, BrowserWindow, dialog, ipcMain, shell } = require('electron');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const APP_DISPLAY_NAME = '月度之星制作助手';
const INPUT_DIR_NAME = '输入图片';
const OUTPUT_DIR_NAME = '输出海报';
const TEMPLATE_NAME = '月度之星个人海报-素材模板4.png';
const README_NAME = '使用说明.txt';

let mainWindow = null;
let activeProcess = null;

function ensureDir(target) {
  fs.mkdirSync(target, { recursive: true });
  return target;
}

function detectFont() {
  const candidates = [
    'C:/Windows/Fonts/msyhbd.ttc',
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simhei.ttf',
  ];
  return candidates.find((candidate) => fs.existsSync(candidate)) || '';
}

function getBackendExecutable() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'backend', 'poster-backend.exe');
  }
  return null;
}

function getBundledTemplatePath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'assets', TEMPLATE_NAME);
  }
  return path.join(app.getAppPath(), TEMPLATE_NAME);
}

function getBundledReadmePath() {
  if (app.isPackaged) {
    return path.join(process.resourcesPath, 'assets', README_NAME);
  }
  return path.join(app.getAppPath(), README_NAME);
}

function getRuntimeRoot() {
  return ensureDir(path.join(app.getPath('documents'), APP_DISPLAY_NAME));
}

function getDefaultState() {
  const runtimeRoot = getRuntimeRoot();
  const inputDir = ensureDir(path.join(runtimeRoot, INPUT_DIR_NAME));
  const outputDir = ensureDir(path.join(runtimeRoot, OUTPUT_DIR_NAME));
  const templatePath = getBundledTemplatePath();
  const fontPath = detectFont();
  const readmeSource = getBundledReadmePath();
  const readmeTarget = path.join(runtimeRoot, README_NAME);

  if (fs.existsSync(readmeSource) && !fs.existsSync(readmeTarget)) {
    fs.copyFileSync(readmeSource, readmeTarget);
  }

  const inputCount = listImageFiles(inputDir).length;
  const outputCount = listImageFiles(outputDir).length;

  return {
    runtimeRoot,
    inputDir,
    outputDir,
    templatePath,
    fontPath,
    readmePath: readmeTarget,
    inputCount,
    outputCount,
    inputFiles: listImageFiles(inputDir),
    outputFiles: listImageFiles(outputDir),
    recentOutputs: listImageFiles(outputDir).slice(0, 5),
    templateExists: fs.existsSync(templatePath),
    backendMode: app.isPackaged ? 'embedded-exe' : 'python-script',
    isRunning: Boolean(activeProcess),
  };
}

function listImageFiles(dirPath) {
  if (!fs.existsSync(dirPath)) {
    return [];
  }

  return fs.readdirSync(dirPath)
    .filter((name) => /\.(png|jpe?g)$/i.test(name))
    .map((name) => {
      const fullPath = path.join(dirPath, name);
      const stats = fs.statSync(fullPath);
      return {
        name,
        fullPath,
        size: stats.size,
        modifiedAt: stats.mtime.toISOString(),
      };
    })
    .sort((a, b) => new Date(b.modifiedAt) - new Date(a.modifiedAt));
}

function sendLog(message, level = 'info') {
  if (!mainWindow || mainWindow.isDestroyed()) {
    return;
  }
  mainWindow.webContents.send('generation-log', {
    level,
    message,
    timestamp: new Date().toISOString(),
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1520,
    height: 940,
    minWidth: 1240,
    minHeight: 760,
    backgroundColor: '#efe9df',
    autoHideMenuBar: true,
    title: APP_DISPLAY_NAME,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadFile(path.join(__dirname, 'index.html'));
}

async function chooseDirectory(currentPath) {
  const result = await dialog.showOpenDialog(mainWindow, {
    defaultPath: currentPath,
    properties: ['openDirectory', 'createDirectory'],
  });

  if (result.canceled || !result.filePaths.length) {
    return currentPath;
  }

  return result.filePaths[0];
}

function startGeneration(options) {
  if (activeProcess) {
    throw new Error('当前已有任务正在运行，请等待完成后再试。');
  }

  const state = {
    ...getDefaultState(),
    ...options,
  };

  ensureDir(state.inputDir);
  ensureDir(state.outputDir);

  const args = [
    '--input', state.inputDir,
    '--output-dir', state.outputDir,
    '--template', state.templatePath,
  ];

  if (state.fontPath) {
    args.push('--font', state.fontPath);
  }

  let command;
  let commandArgs;

  if (app.isPackaged) {
    command = getBackendExecutable();
    commandArgs = args;
  } else {
    command = process.platform === 'win32' ? 'python' : 'python3';
    commandArgs = [path.join(app.getAppPath(), 'batch_generate_posters.py'), ...args];
  }

  sendLog('开始生成海报...', 'info');
  sendLog(`输入目录：${state.inputDir}`, 'muted');
  sendLog(`输出目录：${state.outputDir}`, 'muted');

  activeProcess = spawn(command, commandArgs, {
    cwd: app.isPackaged ? process.resourcesPath : app.getAppPath(),
    windowsHide: true,
  });

  activeProcess.stdout.on('data', (buffer) => {
    buffer.toString('utf8').split(/\r?\n/).filter(Boolean).forEach((line) => sendLog(line, 'info'));
  });

  activeProcess.stderr.on('data', (buffer) => {
    buffer.toString('utf8').split(/\r?\n/).filter(Boolean).forEach((line) => sendLog(line, 'error'));
  });

  activeProcess.on('close', (code) => {
    activeProcess = null;
    sendLog(code === 0 ? '任务已完成。' : `任务结束，退出码：${code}`, code === 0 ? 'success' : 'error');
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('generation-finished', {
        exitCode: code,
        state: getDefaultState(),
      });
    }
  });

  activeProcess.on('error', (error) => {
    activeProcess = null;
    sendLog(`启动失败：${error.message}`, 'error');
  });
}

app.whenReady().then(() => {
  createWindow();

  ipcMain.handle('app:get-state', async () => getDefaultState());
  ipcMain.handle('app:choose-directory', async (_event, currentPath) => chooseDirectory(currentPath));
  ipcMain.handle('app:open-path', async (_event, targetPath) => {
    if (!targetPath) {
      return;
    }
    await shell.openPath(targetPath);
  });
  ipcMain.handle('app:start-generation', async (_event, options) => {
    startGeneration(options);
    return { ok: true };
  });

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
