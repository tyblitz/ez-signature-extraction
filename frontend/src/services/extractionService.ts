export interface ExtractionParams {
  filePath: string;
  inkMode: 'blue' | 'black' | 'auto';
  preservationLevel: number;
  renderMode?: 'natural' | 'stamp';
  multiMode?: boolean;
}

export async function processSignature(params: ExtractionParams): Promise<ExtractionResultPayload> {
  if (window.electronAPI) {
    return await window.electronAPI.extractSignature(params);
  }
  
  // Fallback mock payload for web preview environments
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: false,
        error: 'Desktop Electron environment not detected. Running in web preview mode.'
      });
    }, 500);
  });
}

export async function processMultiSignatureV2(params: ExtractionParams): Promise<any> {
  if (window.electronAPI && window.electronAPI.extractMultiSignatureV2) {
    return await window.electronAPI.extractMultiSignatureV2(params);
  }
  return { success: false, error: 'Desktop Electron environment not detected.' };
}

export async function exportSignaturePng(base64Data: string, defaultName: string = 'transparent_signature.png'): Promise<SaveResultPayload> {
  if (window.electronAPI) {
    return await window.electronAPI.saveSignaturePng({ base64Data, defaultName });
  }

  // Web fallback download
  try {
    const link = document.createElement('a');
    link.href = base64Data;
    link.download = defaultName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    return { success: true };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}

export async function unpackZipArchive(zipPath: string): Promise<{ success: boolean; items?: Array<{ path: string; filename: string; base64: string }>; error?: string }> {
  if (window.electronAPI) {
    return await window.electronAPI.unpackZip({ zipPath });
  }
  return { success: false, error: 'ZIP archive unpacking is only supported in Desktop Electron mode.' };
}

export async function exportBatchZip(transparentItems: Array<{ filename: string; base64: string }>, defaultName: string = 'signatures_batch.zip'): Promise<SaveResultPayload> {
  if (window.electronAPI) {
    return await window.electronAPI.saveBatchZip({ transparentItems, defaultName });
  }
  return { success: false, error: 'Batch ZIP export is only supported in Desktop Electron mode.' };
}

export async function cancelExtraction(): Promise<{ success: boolean; canceled?: boolean }> {
  if (window.electronAPI && window.electronAPI.cancelExtraction) {
    return await window.electronAPI.cancelExtraction();
  }
  return { success: true, canceled: false };
}
