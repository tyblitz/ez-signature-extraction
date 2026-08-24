<template>
  <div class="zoom-controls">
    <button class="btn-zoom" title="Zoom Out" @click="zoomOut">-</button>
    <span class="zoom-level">{{ Math.round(zoomScale * 100) }}%</span>
    <button class="btn-zoom" title="Zoom In" @click="zoomIn">+</button>
    
    <div class="divider"></div>
    
    <button class="btn-preset" :class="{ active: zoomScale === 1.0 }" @click="resetZoom">Fit</button>
    <button class="btn-preset" :class="{ active: zoomScale === 2.0 }" @click="setZoom(2.0)">200%</button>
    <button class="btn-preset" :class="{ active: zoomScale === 4.0 }" @click="setZoom(4.0)">400%</button>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  zoomScale: number;
}>();

const emit = defineEmits<{
  (e: 'update:zoom', value: number): void;
  (e: 'reset'): void;
}>();

function zoomIn() {
  const next = Math.min(8.0, Number((props.zoomScale + 0.25).toFixed(2)));
  emit('update:zoom', next);
}

function zoomOut() {
  const next = Math.max(0.25, Number((props.zoomScale - 0.25).toFixed(2)));
  emit('update:zoom', next);
}

function setZoom(val: number) {
  emit('update:zoom', val);
}

function resetZoom() {
  emit('reset');
}
</script>

<style scoped>
.zoom-controls {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #1e293b;
  border: 1px solid #334155;
  padding: 4px 10px;
  border-radius: 8px;
}

.btn-zoom, .btn-preset {
  background: #0f172a;
  color: #cbd5e1;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-zoom:hover, .btn-preset:hover {
  background: #334155;
  color: #white;
}

.btn-preset.active {
  background: #2563eb;
  color: white;
  border-color: #3b82f6;
}

.zoom-level {
  font-size: 0.8rem;
  font-weight: 600;
  color: #f8fafc;
  min-width: 44px;
  text-align: center;
}

.divider {
  width: 1px;
  height: 16px;
  background: #334155;
  margin: 0 4px;
}
</style>
