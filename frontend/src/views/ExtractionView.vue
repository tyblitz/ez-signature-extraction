<template>
  <div class="app-layout">
    <!-- Header Bar -->
    <header class="app-header">
      <div class="brand">
        <span class="logo-icon">✍️</span>
        <h1 class="app-title">EZ Signature Extraction Engine</h1>
        <span class="version-tag">v1.1.2</span>
      </div>

      <div v-if="activeResult" class="header-actions">
        <button class="btn-export-primary" :disabled="isProcessing" @click="handleExport">
          💾 Download Transparent PNG
        </button>
      </div>
    </header>

    <!-- Workspace Body -->
    <main class="workspace-body">
      <!-- Left Controls Sidebar -->
      <aside class="sidebar">
        <!-- App Mode Switcher (v1.1 Stable vs v1.2 Lab) -->
        <div class="mode-card">
          <label class="mode-card-title">Environment Mode</label>
          <div class="mode-toggle-group">
            <button 
              class="btn-toggle" 
              :class="{ active: envMode === 'v1.1' }" 
              @click="setEnvMode('v1.1')"
            >
              🎯 v1.1 Single-Sig
            </button>
            <button 
              class="btn-toggle" 
              :class="{ active: envMode === 'v1.2' }" 
              @click="setEnvMode('v1.2')"
            >
              👥 v1.2 Multi-Lab
            </button>
          </div>
        </div>

        <!-- File Upload Section -->
        <DropZone 
          :isProcessing="isProcessing"
          @files-selected="onFilesSelected"
        />

        <!-- Batch Queue Component -->
        <BatchQueue 
          v-if="batchQueue.length > 0"
          :queue="batchQueue"
          :activeItemId="activeItemId"
          :isProcessing="isProcessing"
          @select-item="selectQueueItem"
          @remove-item="removeQueueItem"
          @extract-all="extractAllBatch"
          @export-zip="exportBatchZipAction"
          @clear-batch="clearBatchQueue"
          @cancel-processing="cancelExtractionTask"
        />

        <!-- Preservation Controls -->
        <PreservationControl 
          v-if="activeItem"
          v-model:inkMode="inkMode"
          v-model:preservationLevel="preservationLevel"
          @change="onControlChanged"
        />

        <!-- Error Notification -->
        <div v-if="errorMsg" class="error-card">
          <div class="error-header">⚠️ Notice</div>
          <p class="error-text">{{ errorMsg }}</p>
        </div>
      </aside>

      <!-- Main Comparison Workspace -->
      <section class="main-content">
        <!-- v1.2 Multi-Signature Lab Isolated View -->
        <MultiExtractionView 
          v-if="envMode === 'v1.2'" 
          :activeResult="activeResult" 
        />

        <!-- v1.1 Stable Single-Signature View -->
        <template v-else>
          <div v-if="!activeResult" class="empty-state">
            <div class="empty-icon">📁</div>
            <h2>Select or drop documents / .ZIP archive to begin</h2>
            <p>Handwritten blue/black signatures will be automatically isolated with 1-to-1 transparent PNG output.</p>
          </div>

          <ComparisonViewer 
            v-else
            :originalSrc="activeResult.original_base64 || ''"
            :transparentSrc="activeResult.transparent_base64 || ''"
            :confidence="activeResult.confidence"
            :metadata="activeResult.metadata"
          />
        </template>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import DropZone from '../components/DropZone.vue';
import BatchQueue, { QueueItem } from '../components/BatchQueue.vue';
import PreservationControl from '../components/PreservationControl.vue';
import ComparisonViewer from '../components/ComparisonViewer.vue';
import MultiExtractionView from './MultiExtractionView.vue';
import { processSignature, processMultiSignatureV2, exportSignaturePng, unpackZipArchive, exportBatchZip, cancelExtraction } from '../services/extractionService';

const isProcessing = ref<boolean>(false);
const errorMsg = ref<string>('');

const envMode = ref<'v1.1' | 'v1.2'>('v1.1');
const inkMode = ref<'blue' | 'black' | 'auto'>('blue');
const preservationLevel = ref<number>(0.5);

const batchQueue = ref<QueueItem[]>([]);
const activeItemId = ref<string>('');

async function setEnvMode(mode: 'v1.1' | 'v1.2') {
  if (envMode.value === mode) return;
  if (isProcessing.value) {
    await cancelExtractionTask();
  }
  envMode.value = mode;
  clearBatchQueue();
}

const activeItem = computed(() => {
  return batchQueue.value.find(i => i.id === activeItemId.value) || null;
});

const activeResult = computed(() => {
  return activeItem.value?.result || null;
});

async function onFilesSelected(items: Array<{ file: File; path: string }>) {
  errorMsg.value = '';
  // Reset queue to show only the new batch
  batchQueue.value = [];
  activeItemId.value = '';

  for (const item of items) {
    const ext = item.file.name.split('.').pop()?.toLowerCase() || '';

    if (ext === 'zip') {
      // Unpack ZIP archive
      isProcessing.value = true;
      try {
        const zipRes = await unpackZipArchive(item.path);
        if (zipRes.success && zipRes.items) {
          for (const zipItem of zipRes.items) {
            addQueueItem(zipItem.path, zipItem.filename, zipItem.base64);
          }
        } else {
          errorMsg.value = zipRes.error || 'Failed to unpack ZIP archive.';
        }
      } catch (err: any) {
        errorMsg.value = err.message || 'ZIP extraction error.';
      } finally {
        isProcessing.value = false;
      }
    } else {
      // Add individual image file
      const thumb = URL.createObjectURL(item.file);
      addQueueItem(item.path, item.file.name, thumb);
    }
  }

  if (batchQueue.value.length > 0) {
    await extractAllBatch();
  }
}

function addQueueItem(filePath: string, filename: string, thumbnail?: string) {
  const id = 'item_' + Math.random().toString(36).substr(2, 9);
  batchQueue.value.push({
    id,
    filePath,
    filename,
    thumbnail,
    status: 'queued'
  });
}

async function selectQueueItem(id: string) {
  activeItemId.value = id;
  const item = batchQueue.value.find(i => i.id === id);
  if (item && (item.status === 'queued' || item.status === 'failed' || !item.result)) {
    await extractSingleItem(id);
  }
}

function removeQueueItem(id: string) {
  if (isProcessing.value) return;
  const idx = batchQueue.value.findIndex(i => i.id === id);
  if (idx !== -1) {
    batchQueue.value.splice(idx, 1);
    if (activeItemId.value === id) {
      activeItemId.value = batchQueue.value.length > 0 ? batchQueue.value[0].id : '';
    }
  }
}

function clearBatchQueue() {
  if (isProcessing.value) return;
  batchQueue.value = [];
  activeItemId.value = '';
  errorMsg.value = '';
}

async function cancelExtractionTask() {
  await cancelExtraction();
  isProcessing.value = false;
  const currentItem = batchQueue.value.find(i => i.id === activeItemId.value);
  if (currentItem && currentItem.status === 'processing') {
    currentItem.status = 'failed';
    currentItem.error = 'Extraction cancelled by user.';
  }
  errorMsg.value = 'Extraction task cancelled.';
}

async function extractSingleItemInternal(id: string) {
  const item = batchQueue.value.find(i => i.id === id);
  if (!item) return;

  item.status = 'processing';
  errorMsg.value = '';

  try {
    const res = envMode.value === 'v1.2'
      ? await processMultiSignatureV2({
          filePath: item.filePath,
          inkMode: inkMode.value,
          preservationLevel: preservationLevel.value
        })
      : await processSignature({
          filePath: item.filePath,
          inkMode: inkMode.value,
          preservationLevel: preservationLevel.value,
          renderMode: 'natural'
        });

    if (res.success) {
      if (envMode.value === 'v1.2' && res.crops && res.crops.length > 0) {
        const baseName = item.filename.split('.')[0];
        const newQueueItems: QueueItem[] = res.crops.map((crop: any) => ({
          id: 'crop_' + Math.random().toString(36).substr(2, 9),
          filePath: item.filePath,
          filename: `${baseName} - ${crop.label}.png`,
          thumbnail: crop.transparent_base64,
          status: 'done',
          result: {
            success: true,
            original_base64: res.original_base64,
            transparent_base64: crop.transparent_base64,
            confidence: crop.confidence,
            metadata: {
              signature_pixels_preserved: crop.preserved_pixels,
              background_pixels_removed: crop.background_pixels,
              ink_mode: inkMode.value,
              preservation_level: preservationLevel.value
            },
            crop_info: crop,
            all_crops: res.crops
          }
        }));
        batchQueue.value = newQueueItems;
        if (newQueueItems.length > 0) {
          activeItemId.value = newQueueItems[0].id;
        }
      } else {
        item.status = 'done';
        item.result = res;
        if (!item.thumbnail && res.original_base64) {
          item.thumbnail = res.original_base64;
        }
      }
    } else {
      item.status = 'failed';
      item.error = res.error || 'Extraction failed.';
      errorMsg.value = res.error || 'Failed to extract signature.';
    }
  } catch (err: any) {
    item.status = 'failed';
    item.error = err.message || 'Unexpected error.';
    errorMsg.value = err.message || 'Processing error.';
  }
}

async function extractSingleItem(id: string) {
  if (isProcessing.value) return;
  isProcessing.value = true;
  try {
    await extractSingleItemInternal(id);
  } finally {
    isProcessing.value = false;
  }
}

async function extractAllBatch() {
  if (isProcessing.value || batchQueue.value.length === 0) return;

  isProcessing.value = true;
  try {
    for (const item of batchQueue.value) {
      activeItemId.value = item.id;
      await extractSingleItemInternal(item.id);
    }
  } finally {
    isProcessing.value = false;
  }
}

function onControlChanged() {
  if (activeItemId.value) {
    extractSingleItem(activeItemId.value);
  }
}

async function handleExport() {
  if (!activeResult.value || !activeResult.value.transparent_base64) return;
  const defaultName = activeItem.value?.filename 
    ? `${activeItem.value.filename.split('.')[0]}_transparent.png`
    : 'transparent_signature.png';

  const res = await exportSignaturePng(activeResult.value.transparent_base64, defaultName);
  if (!res.success && !res.canceled) {
    alert(`Export failed: ${res.error}`);
  }
}

async function exportBatchZipAction() {
  const doneItems = batchQueue.value.filter(i => i.status === 'done' && i.result?.transparent_base64);
  if (doneItems.length === 0) return;

  const transparentItems = doneItems.map(i => ({
    filename: i.filename,
    base64: i.result.transparent_base64
  }));

  const res = await exportBatchZip(transparentItems, 'signatures_batch.zip');
  if (!res.success && !res.canceled) {
    alert(`Batch ZIP export failed: ${res.error}`);
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  background-color: #0f172a;
  color: #f8fafc;
  overflow: hidden;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
  height: 60px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 1.5rem;
}

.app-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
  color: #f1f5f9;
  letter-spacing: -0.01em;
}

.version-tag {
  font-size: 0.75rem;
  background-color: #334155;
  color: #94a3b8;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-export-primary {
  background-color: #10b981;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-export-primary:hover:not(:disabled) {
  background-color: #059669;
}

.btn-export-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.workspace-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}

.sidebar {
  width: 320px;
  min-width: 260px;
  max-width: 340px;
  flex-shrink: 0;
  background-color: #0f172a;
  border-right: 1px solid #334155;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #334155 #0f172a;
}

.mode-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.mode-card-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #cbd5e1;
}

.mode-toggle-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.btn-toggle {
  background: #0f172a;
  color: #94a3b8;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 6px 4px;
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn-toggle:hover {
  background: #334155;
  color: #f8fafc;
}

.btn-toggle.active {
  background: #2563eb;
  color: white;
  border-color: #3b82f6;
}

.main-content {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  background-color: #020617;
  overflow: hidden;
  min-width: 0;
}

.empty-state {
  margin: auto;
  text-align: center;
  max-width: 420px;
  color: #64748b;
}

.empty-icon {
  font-size: 3.5rem;
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-state h2 {
  font-size: 1.2rem;
  color: #94a3b8;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 0.85rem;
  line-height: 1.5;
}

.error-card {
  background-color: #7f1d1d40;
  border: 1px solid #991b1b;
  border-radius: 8px;
  padding: 12px;
}

.error-header {
  font-size: 0.8rem;
  font-weight: 700;
  color: #fca5a5;
  margin-bottom: 4px;
}

.error-text {
  font-size: 0.75rem;
  color: #fecaca;
  margin: 0;
}

.btn-switch-multi {
  margin-top: 8px;
  width: 100%;
  padding: 6px 10px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.btn-switch-multi:hover {
  background: #2563eb;
}

/* Responsive Breakpoints */
@media (max-width: 1080px) {
  .sidebar {
    width: 280px;
    padding: 10px;
    gap: 10px;
  }

  .main-content {
    padding: 10px;
  }
}

@media (max-width: 820px) {
  .workspace-body {
    flex-direction: column;
    overflow-y: auto;
  }

  .sidebar {
    width: 100%;
    max-width: 100%;
    border-right: none;
    border-bottom: 1px solid #334155;
    overflow-y: visible;
  }

  .main-content {
    min-height: 550px;
    overflow: visible;
  }
}
</style>
