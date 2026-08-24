<template>
  <div 
    class="drop-zone-container"
    :class="{ 'is-dragover': isDragOver, 'has-file': selectedFile }"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
  >
    <input 
      type="file" 
      ref="fileInput" 
      class="file-input-hidden" 
      accept=".jpg,.jpeg,.png,.webp,.bmp,.zip,image/jpeg,image/png,image/webp,application/zip"
      multiple
      @change="onFileSelected"
    />

    <div class="drop-prompt">
      <div class="icon-circle">
        <svg class="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
        </svg>
      </div>

      <h3 class="drop-title">Drag and drop documents or ZIP archive</h3>
      <p class="drop-subtitle">Supports JPG, PNG, WEBP, and .ZIP archives (Multiple files allowed)</p>

      <button 
        class="btn-browse" 
        :disabled="isProcessing" 
        @click="triggerFileInput"
      >
        <span v-if="isProcessing">⚙️ Processing Batch...</span>
        <span v-else>Browse Files / ZIP</span>
      </button>

      <p v-if="errorMessage" class="error-banner">
        ⚠️ {{ errorMessage }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  isProcessing?: boolean;
}>();

const emit = defineEmits<{
  (e: 'files-selected', items: Array<{ file: File; path: string }>): void;
  (e: 'process'): void;
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const isDragOver = ref(false);
const errorMessage = ref<string>('');

const ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'zip'];
const MAX_SIZE_BYTES = 100 * 1024 * 1024; // 100MB

function triggerFileInput() {
  fileInput.value?.click();
}

function processFiles(fileList: FileList | File[]) {
  errorMessage.value = '';
  const validItems: Array<{ file: File; path: string }> = [];

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i];
    const ext = file.name.split('.').pop()?.toLowerCase() || '';

    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      continue;
    }

    if (file.size > MAX_SIZE_BYTES) {
      continue;
    }

    const path = (file as any).path || file.name;
    validItems.push({ file, path });
  }

  if (validItems.length === 0) {
    errorMessage.value = 'No supported document images or ZIP archives were found.';
    return;
  }

  emit('files-selected', validItems);
  if (fileInput.value) fileInput.value.value = '';
}

function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    processFiles(target.files);
  }
}

function onDragOver() {
  isDragOver.value = true;
}

function onDragLeave() {
  isDragOver.value = false;
}

function onDrop(event: DragEvent) {
  isDragOver.value = false;
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    processFiles(event.dataTransfer.files);
  }
}

function removeFile() {
  selectedFile.value = null;
  selectedFilePath.value = '';
  errorMessage.value = '';
  if (fileInput.value) fileInput.value.value = '';
}

function emitProcess() {
  if (selectedFile.value) {
    emit('process');
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
</script>

<style scoped>
.file-input-hidden {
  display: none !important;
  opacity: 0;
  position: absolute;
  pointer-events: none;
}

.drop-zone-container {
  border: 2px dashed #334155;
  border-radius: 12px;
  background-color: #1e293b40;
  padding: 16px 12px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.drop-prompt {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  text-align: center;
}

.icon-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #3b82f61a;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.upload-icon {
  width: 24px;
  height: 24px;
  color: #60a5fa;
}

.drop-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #f1f5f9;
}

.drop-subtitle {
  margin: 0;
  font-size: 0.75rem;
  color: #94a3b8;
}

.btn-browse {
  margin-top: 4px;
  padding: 6px 16px;
  background-color: #3b82f6;
  color: #ffffff;
  font-weight: 500;
  font-size: 0.8rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.btn-browse:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-browse:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-banner {
  margin-top: 8px;
  font-size: 0.75rem;
  color: #ef4444;
  background: #ef44441a;
  padding: 4px 10px;
  border-radius: 6px;
}

.file-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #0f172a;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #334155;
}

.file-icon {
  font-size: 1.5rem;
}

.file-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  flex: 1;
  overflow: hidden;
}

.file-name {
  font-weight: 500;
  font-size: 0.9rem;
  color: #f8fafc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.file-size {
  font-size: 0.75rem;
  color: #94a3b8;
}

.btn-remove {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1rem;
  cursor: pointer;
  padding: 4px;
}

.btn-remove:hover {
  color: #f8fafc;
}

.btn-extract {
  padding: 12px;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  font-weight: 600;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: opacity 0.15s ease;
}

.btn-extract:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff40;
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
