import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import path from 'path';
import { spawn } from 'child_process';
import fs from 'fs';

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 850,
    minWidth: 1024,
    minHeight: 700,
    title: 'EZ Signature Extraction Engine',
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    }
  });

  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

let activePyProcess: any = null;

function getBackendCommand(): { command: string; baseArgs: string[]; cwd: string } {
  const projectRoot = path.resolve(__dirname, '..');
  const exeName = process.platform === 'win32' ? 'ez_backend.exe' : 'ez_backend';

  // 1. Packaged Electron App (resources/backend/ez_backend/ez_backend.exe)
  const packagedExe = path.join(process.resourcesPath, 'backend', 'ez_backend', exeName);
  if (fs.existsSync(packagedExe)) {
    return { command: packagedExe, baseArgs: [], cwd: path.dirname(packagedExe) };
  }

  // 2. Local PyInstaller build (backend_dist/ez_backend/ez_backend.exe)
  const localExe = path.join(projectRoot, 'backend_dist', 'ez_backend', exeName);
  if (fs.existsSync(localExe)) {
    return { command: localExe, baseArgs: [], cwd: projectRoot };
  }

  // 3. Workspace venv Python fallback
  const venvPythonWin = path.join(projectRoot, 'venv', 'Scripts', 'python.exe');
  const pythonExecutable = fs.existsSync(venvPythonWin) ? venvPythonWin : 'python';
  return { command: pythonExecutable, baseArgs: ['-m', 'backend.main'], cwd: projectRoot };
}

// IPC Handler: Extract Signature via Python subprocess
ipcMain.handle('extract-signature', async (event, args) => {
  const { filePath, inkMode = 'blue', preservationLevel = 0.5, renderMode = 'natural', multiMode = false } = args;

  return new Promise((resolve) => {
    const { command, baseArgs, cwd } = getBackendCommand();

    const cmdArgs = [
      ...baseArgs,
      filePath,
      '--json',
      '--ink-mode', String(inkMode),
      '--preservation', String(preservationLevel),
      '--render-mode', String(renderMode)
    ];

    if (multiMode) {
      cmdArgs.push('--multi');
    }

    const pyProcess = spawn(command, cmdArgs, { cwd });
    activePyProcess = pyProcess;

    let stdoutData = '';
    let stderrData = '';

    pyProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    pyProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
    });

    pyProcess.on('close', (code) => {
      activePyProcess = null;
      if (stdoutData.trim()) {
        try {
          const parsed = JSON.parse(stdoutData.trim());
          resolve(parsed);
          return;
        } catch (e) {
          // stdout JSON parsing error fallback
        }
      }

      resolve({
        success: false,
        error: stderrData || `Backend process exited with code ${code}`
      });
    });

    pyProcess.on('error', (err) => {
      activePyProcess = null;
      resolve({
        success: false,
        error: `Failed to spawn backend process: ${err.message}`
      });
    });
  });
});

// IPC Handler: Extract Multi-Signature V2 (Lab Mode)
ipcMain.handle('extract-multi-signature-v2', async (event, args) => {
  const { filePath, inkMode = 'blue', preservationLevel = 0.5 } = args;

  return new Promise((resolve) => {
    const { command, baseArgs, cwd } = getBackendCommand();

    const cmdArgs = [
      ...baseArgs,
      filePath,
      '--json',
      '--multi-v2',
      '--ink-mode', String(inkMode),
      '--preservation', String(preservationLevel)
    ];

    const pyProcess = spawn(command, cmdArgs, { cwd });
    activePyProcess = pyProcess;

    let stdoutData = '';
    let stderrData = '';

    pyProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    pyProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
    });

    pyProcess.on('close', (code) => {
      activePyProcess = null;
      if (stdoutData.trim()) {
        try {
          const parsed = JSON.parse(stdoutData.trim());
          resolve(parsed);
          return;
        } catch (e) {
          // JSON parse error fallback
        }
      }

      resolve({
        success: false,
        error: stderrData || `Backend process exited with code ${code}`
      });
    });

    pyProcess.on('error', (err) => {
      activePyProcess = null;
      resolve({
        success: false,
        error: err.message
      });
    });
  });
});

// IPC Handler: Cancel active extraction process
ipcMain.handle('cancel-extraction', async () => {
  if (activePyProcess) {
    try {
      activePyProcess.kill('SIGKILL');
    } catch (e) {}
    activePyProcess = null;
    return { success: true, canceled: true };
  }
  return { success: true, canceled: false };
});

// IPC Handler: Native Save File Dialog for PNG export
ipcMain.handle('save-signature-png', async (event, { base64Data, defaultName = 'transparent_signature.png' }) => {
  if (!mainWindow) return { success: false, error: 'No active window' };

  const { filePath, canceled } = await dialog.showSaveDialog(mainWindow, {
    title: 'Export Transparent Signature',
    defaultPath: defaultName,
    filters: [{ name: 'PNG Images', extensions: ['png'] }]
  });

  if (canceled || !filePath) {
    return { success: false, canceled: true };
  }

  try {
    const base64Image = base64Data.replace(/^data:image\/png;base64,/, '');
    fs.writeFileSync(filePath, Buffer.from(base64Image, 'base64'));
    return { success: true, filePath };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
});

// IPC Handler: Unpack ZIP archive
ipcMain.handle('unpack-zip', async (event, { zipPath }) => {
  return new Promise((resolve) => {
    const projectRoot = path.resolve(__dirname, '..');
    const venvPythonWin = path.join(projectRoot, 'venv', 'Scripts', 'python.exe');
    const pythonExecutable = fs.existsSync(venvPythonWin) ? venvPythonWin : 'python';

    const cmdArgs = ['-m', 'backend.main', 'dummy.png', '--unpack-zip', zipPath];
    const pyProcess = spawn(pythonExecutable, cmdArgs, { cwd: projectRoot });

    let stdoutData = '';
    let stderrData = '';

    pyProcess.stdout.on('data', (data) => { stdoutData += data.toString(); });
    pyProcess.stderr.on('data', (data) => { stderrData += data.toString(); });

    pyProcess.on('close', () => {
      if (stdoutData.trim()) {
        try {
          resolve(JSON.parse(stdoutData.trim()));
          return;
        } catch (e) {}
      }
      resolve({ success: false, error: stderrData || 'Failed to unpack ZIP archive.' });
    });
  });
});

// IPC Handler: Save Batch ZIP Archive
ipcMain.handle('save-batch-zip', async (event, { transparentItems, defaultName = 'signatures_batch.zip' }) => {
  if (!mainWindow) return { success: false, error: 'No active window' };

  const { filePath, canceled } = await dialog.showSaveDialog(mainWindow, {
    title: 'Export Batch Signatures ZIP',
    defaultPath: defaultName,
    filters: [{ name: 'ZIP Archives', extensions: ['zip'] }]
  });

  if (canceled || !filePath) {
    return { success: false, canceled: true };
  }

  try {
    // Create temporary directory with extracted transparent PNG files
    const tempDir = fs.mkdtempSync(path.join(app.getPath('temp'), 'ez_batch_'));
    const tempFilePaths: string[] = [];

    for (let i = 0; i < transparentItems.length; i++) {
      const item = transparentItems[i];
      const filename = item.filename ? item.filename.replace(/\.[^/.]+$/, '') + '_transparent.png' : `signature_${i + 1}.png`;
      const itemPath = path.join(tempDir, filename);
      const base64Data = item.base64.replace(/^data:image\/png;base64,/, '');
      fs.writeFileSync(itemPath, Buffer.from(base64Data, 'base64'));
      tempFilePaths.push(itemPath);
    }

    return new Promise((resolve) => {
      const projectRoot = path.resolve(__dirname, '..');
      const venvPythonWin = path.join(projectRoot, 'venv', 'Scripts', 'python.exe');
      const pythonExecutable = fs.existsSync(venvPythonWin) ? venvPythonWin : 'python';

      const cmdArgs = ['-m', 'backend.main', 'dummy.png', '--create-zip', filePath, '--files', ...tempFilePaths];
      const pyProcess = spawn(pythonExecutable, cmdArgs, { cwd: projectRoot });

      let stdoutData = '';
      pyProcess.stdout.on('data', (data) => { stdoutData += data.toString(); });

      pyProcess.on('close', () => {
        if (stdoutData.trim()) {
          try {
            const res = JSON.parse(stdoutData.trim());
            resolve({ success: res.success, filePath: res.zip_path, error: res.error });
            return;
          } catch (e) {}
        }
        resolve({ success: true, filePath });
      });
    });
  } catch (err: any) {
    return { success: false, error: err.message };
  }
});
