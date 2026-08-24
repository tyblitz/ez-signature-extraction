/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ExtractionResultPayload {
  success: boolean;
  error?: string | null;
  input_filename?: string;
  original_base64?: string;
  transparent_base64?: string;
  transparent_output_path?: string;
  confidence?: number;
  bounding_box?: { x: number; y: number; width: number; height: number };
  metadata?: {
    signature_pixels_preserved: number;
    background_pixels_removed: number;
    ink_mode: string;
    preservation_level: number;
  };
}

interface SaveResultPayload {
  success: boolean;
  filePath?: string;
  canceled?: boolean;
  error?: string;
}

interface Window {
  electronAPI?: {
    extractSignature: (payload: { filePath: string; inkMode?: string; preservationLevel?: number }) => Promise<ExtractionResultPayload>;
    saveSignaturePng: (payload: { base64Data: string; defaultName?: string }) => Promise<SaveResultPayload>;
  };
}
