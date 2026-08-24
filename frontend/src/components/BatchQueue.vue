<template>
  <div class="batch-queue-container">
    <div class="queue-header">
      <div class="title-row">
        <h3 class="queue-title">Batch Queue</h3>
        <div class="header-right">
          <span class="count-badge">{{ queue.length }} files</span>
          <button 
            v-if="queue.length > 0" 
            class="btn-clear-batch" 
            :disabled="isProcessing" 
            title="Clear entire batch queue"
            @click="$emit('clear-batch')"
          >
            🗑️ Clear
          </button>
        </div>
      </div>

      <div v-if="queue.length > 0" class="progress-bar-track">
        <div 
          class="progress-bar-fill"
          :style="{ width: progressPercent + '%' }"
        ></div>
      </div>
    </div>

    <!-- Batch Action Buttons -->
    <div v-if="queue.length > 0" class="queue-actions">
      <button 
        class="btn-action primary" 
        :disabled="isProcessing" 
        @click="$emit('extract-all')"
      >
        <span v-if="isProcessing" class="spinner"></span>
        <span>{{ isProcessing ? 'Extracting Batch...' : (hasCompletedItems ? '⚡ Re-Extract All Signatures' : '⚡ Extract All Signatures') }}</span>
      </button>

      <button 
        v-if="isProcessing" 
        class="btn-action cancel" 
        @click="$emit('cancel-processing')"
      >
        🚫 Cancel Processing
      </button>

      <button 
        v-if="hasCompletedItems && !isProcessing" 
        class="btn-action secondary" 
        :disabled="isProcessing"
        @click="$emit('export-zip')"
      >
        📦 Download All as ZIP
      </button>
    </div>

    <!-- Items List -->
    <div class="queue-list">
      <div v-if="queue.length === 0" class="queue-empty">
        <span>No items in queue</span>
      </div>

      <div 
        v-for="(item, index) in queue" 
        :key="item.id"
        class="queue-item"
        :class="{ active: item.id === activeItemId, [item.status]: true }"
        @click="$emit('select-item', item.id)"
      >
        <div class="item-icon">
          <img v-if="item.thumbnail" :src="item.thumbnail" alt="thumb" class="thumb-img" />
          <span v-else>📄</span>
        </div>

        <div class="item-details">
          <span class="item-filename" :title="item.filename">{{ item.filename }}</span>
          <span class="status-tag" :class="item.status">
            {{ getStatusText(item.status) }}
          </span>
        </div>

        <button 
          class="btn-remove-item" 
          title="Remove item"
          @click.stop="$emit('remove-item', item.id)"
        >
          ✕
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export interface QueueItem {
  id: string;
  filePath: string;
  filename: string;
  thumbnail?: string;
  status: 'queued' | 'processing' | 'done' | 'failed';
  result?: any;
  error?: string;
}

const props = defineProps<{
  queue: QueueItem[];
  activeItemId: string;
  isProcessing: boolean;
}>();

defineEmits<{
  (e: 'select-item', id: string): void;
  (e: 'remove-item', id: string): void;
  (e: 'extract-all'): void;
  (e: 'export-zip'): void;
  (e: 'clear-batch'): void;
  (e: 'cancel-processing'): void;
}>();

const completedCount = computed(() => {
  return props.queue.filter(i => i.status === 'done' || i.status === 'failed').length;
});

const hasCompletedItems = computed(() => {
  return props.queue.some(i => i.status === 'done');
});

const progressPercent = computed(() => {
  if (props.queue.length === 0) return 0;
  return Math.round((completedCount.value / props.queue.length) * 100);
});

function getStatusText(status: string) {
  switch (status) {
    case 'processing': return '⚙️ Processing';
    case 'done': return '✅ Done';
    case 'failed': return '❌ Failed';
    default: return '⏳ Queued';
  }
}
</script>

<style scoped>
.batch-queue-container {
  display: flex;
  flex-direction: column;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  overflow: hidden;
}

.queue-header {
  padding: 12px 14px;
  background: #0f172a;
  border-bottom: 1px solid #334155;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.queue-title {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 700;
  color: #f1f5f9;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-badge {
  font-size: 0.75rem;
  background: #334155;
  color: #94a3b8;
  padding: 2px 8px;
  border-radius: 10px;
}

.btn-clear-batch {
  background: #ef44441a;
  color: #f87171;
  border: 1px solid #ef444440;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-clear-batch:hover:not(:disabled) {
  background: #ef444433;
  color: #fca5a5;
}

.btn-clear-batch:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.progress-bar-track {
  height: 4px;
  background: #334155;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #2563eb, #38bdf8);
  transition: width 0.3s ease;
}

.queue-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  background: #1e293b;
  border-bottom: 1px solid #334155;
}

.btn-action {
  width: 100%;
  padding: 8px 12px;
  font-size: 0.8rem;
  font-weight: 600;
  border-radius: 6px;
  cursor: pointer;
  border: none;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn-action.primary {
  background: #2563eb;
  color: white;
}

.btn-action.primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-action.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-action.secondary {
  background: #059669;
  color: white;
}

.btn-action.secondary:hover:not(:disabled) {
  background: #047857;
}

.btn-action.secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-action.cancel {
  background: #dc2626;
  color: white;
}

.btn-action.cancel:hover {
  background: #b91c1c;
}

.queue-list {
  max-height: 260px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.queue-empty {
  padding: 20px;
  text-align: center;
  font-size: 0.8rem;
  color: #64748b;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-bottom: 1px solid #33415540;
  cursor: pointer;
  transition: background 0.15s ease;
}

.queue-item:hover {
  background: #33415560;
}

.queue-item.active {
  background: #2563eb20;
  border-left: 3px solid #3b82f6;
}

.item-icon {
  width: 28px;
  height: 28px;
  border-radius: 4px;
  background: #0f172a;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  overflow: hidden;
}

.thumb-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.item-filename {
  font-size: 0.75rem;
  color: #e2e8f0;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-tag {
  font-size: 0.65rem;
  font-weight: 600;
}

.status-tag.queued { color: #94a3b8; }
.status-tag.processing { color: #38bdf8; }
.status-tag.done { color: #34d399; }
.status-tag.failed { color: #f87171; }

.btn-remove-item {
  background: transparent;
  border: none;
  color: #64748b;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
}

.btn-remove-item:hover {
  color: #ef4444;
  background: #ef444420;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 2px solid #ffffff40;
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
