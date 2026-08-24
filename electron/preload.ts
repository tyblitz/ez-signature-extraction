import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  extractSignature: (payload: { filePath: string; inkMode?: string; preservationLevel?: number; renderMode?: string }) =>
    ipcRenderer.invoke('extract-signature', payload),
  extractMultiSignatureV2: (payload: { filePath: string; inkMode?: string; preservationLevel?: number }) =>
    ipcRenderer.invoke('extract-multi-signature-v2', payload),
  saveSignaturePng: (payload: { base64Data: string; defaultName?: string }) =>
    ipcRenderer.invoke('save-signature-png', payload),
  unpackZip: (payload: { zipPath: string }) =>
    ipcRenderer.invoke('unpack-zip', payload),
  saveBatchZip: (payload: { transparentItems: Array<{ filename: string; base64: string }>; defaultName?: string }) =>
    ipcRenderer.invoke('save-batch-zip', payload),
  cancelExtraction: () =>
    ipcRenderer.invoke('cancel-extraction')
});
