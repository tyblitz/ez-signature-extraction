<template>
  <div class="comparison-viewer">
    <div class="viewer-header">
      <div class="view-mode-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: viewMode === 'split' }" 
          @click="viewMode = 'split'"
        >
          ↔️ Side-by-Side
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: viewMode === 'transparent' }" 
          @click="viewMode = 'transparent'"
        >
          ✨ Extracted Only
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: viewMode === 'original' }" 
          @click="viewMode = 'original'"
        >
          📄 Original Only
        </button>
      </div>

      <ZoomControls 
        :zoomScale="zoomScale"
        @update:zoom="onZoomUpdate"
        @reset="resetTransform"
      />
    </div>

    <div class="viewer-body" :class="viewMode">
      <!-- Original Document View -->
      <div 
        v-if="viewMode === 'split' || viewMode === 'original'" 
        class="panel original-panel"
      >
        <div class="panel-badge">Original Document</div>
        <div 
          class="canvas-viewport light-paper"
          @mousedown="startPan"
          @mousemove="onPan"
          @mouseup="endPan"
          @mouseleave="endPan"
          @wheel.prevent="onWheel"
        >
          <div class="image-wrapper" :style="transformStyle">
            <img :src="originalSrc" alt="Original Document" class="preview-img" @dragstart.prevent />
          </div>
        </div>
      </div>

      <!-- Extracted Signature View -->
      <div 
        v-if="viewMode === 'split' || viewMode === 'transparent'" 
        class="panel transparent-panel"
      >
        <TransparencyViewer 
          :imageSrc="transparentSrc"
          :zoomScale="zoomScale"
          :panX="panX"
          :panY="panY"
          @update:pan="onPanUpdate"
          @update:zoom="onZoomUpdate"
        />
      </div>
    </div>

    <!-- Metadata Footer -->
    <div v-if="metadata" class="viewer-footer">
      <div class="stat-item">
        <span class="stat-label">Preserved Pixels:</span>
        <span class="stat-value text-green">{{ metadata.signature_pixels_preserved.toLocaleString() }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Background Removed:</span>
        <span class="stat-value text-blue">{{ metadata.background_pixels_removed.toLocaleString() }}</span>
      </div>
      <div v-if="confidence !== undefined" class="stat-item">
        <span class="stat-label">Detection Confidence:</span>
        <span class="stat-value text-sky">{{ Math.round(confidence * 100) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import TransparencyViewer from './TransparencyViewer.vue';
import ZoomControls from './ZoomControls.vue';

const props = defineProps<{
  originalSrc: string;
  transparentSrc: string;
  confidence?: number;
  metadata?: {
    signature_pixels_preserved: number;
    background_pixels_removed: number;
    ink_mode: string;
    preservation_level: number;
  };
}>();

const viewMode = ref<'split' | 'transparent' | 'original'>('split');
const zoomScale = ref<number>(1.0);
const panX = ref<number>(0);
const panY = ref<number>(0);

const isPanning = ref(false);
const startMouseX = ref(0);
const startMouseY = ref(0);
const initialPanX = ref(0);
const initialPanY = ref(0);

const transformStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoomScale.value})`,
  transformOrigin: 'center center'
}));

function onZoomUpdate(newZoom: number) {
  zoomScale.value = newZoom;
}

function onWheel(event: WheelEvent) {
  const delta = event.deltaY < 0 ? 0.15 : -0.15;
  zoomScale.value = Math.min(8.0, Math.max(0.25, Number((zoomScale.value + delta).toFixed(2))));
}

function resetTransform() {
  zoomScale.value = 1.0;
  panX.value = 0;
  panY.value = 0;
}

function onPanUpdate(payload: { x: number; y: number }) {
  panX.value = payload.x;
  panY.value = payload.y;
}

function startPan(event: MouseEvent) {
  isPanning.value = true;
  startMouseX.value = event.clientX;
  startMouseY.value = event.clientY;
  initialPanX.value = panX.value;
  initialPanY.value = panY.value;
}

function onPan(event: MouseEvent) {
  if (!isPanning.value) return;
  const dx = event.clientX - startMouseX.value;
  const dy = event.clientY - startMouseY.value;
  panX.value = initialPanX.value + dx;
  panY.value = initialPanY.value + dy;
}

function endPan() {
  isPanning.value = false;
}
</script>

<style scoped>
.comparison-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  gap: 8px;
  min-height: 0;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  background: #1e293b;
  padding: 8px 12px;
  border-radius: 8px;
  border: 1px solid #334155;
  flex-shrink: 0;
}

.view-mode-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tab-btn {
  background: #0f172a;
  color: #cbd5e1;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  background: #334155;
  color: white;
}

.tab-btn.active {
  background: #2563eb;
  color: white;
  border-color: #3b82f6;
}

.viewer-body {
  flex: 1;
  display: flex;
  gap: 12px;
  min-height: 0;
  height: 100%;
}

.viewer-body.split .panel {
  flex: 1;
}

.viewer-body.transparent .panel.transparent-panel,
.viewer-body.original .panel.original-panel {
  flex: 1;
}

@media (max-width: 900px) {
  .viewer-body.split {
    flex-direction: column;
  }
}

.panel {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #334155;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.panel-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
  background: #020617cc;
  color: #e2e8f0;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 6px;
  border: 1px solid #334155;
  backdrop-filter: blur(4px);
}

.canvas-viewport {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
  cursor: grab;
  user-select: none;
  width: 100%;
  height: 100%;
  min-height: 0;
}

.canvas-viewport.light-paper {
  background: #f1f5f9;
}

.image-wrapper {
  transition: transform 0.05s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 100%;
  height: 100%;
}

.bbox-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.bbox-rect {
  position: absolute;
  border: 2px dashed #3b82f6;
  background-color: #3b82f61a;
  border-radius: 4px;
  cursor: pointer;
  pointer-events: auto;
  transition: all 0.15s ease;
}

.bbox-rect:hover {
  border-color: #60a5fa;
  background-color: #3b82f633;
}

.bbox-rect.active {
  border: 2.5px solid #10b981;
  background-color: #10b98126;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.4);
}

.bbox-tag {
  position: absolute;
  top: -22px;
  left: 0;
  background: #10b981;
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 3px;
  white-space: nowrap;
}

.bbox-rect:not(.active) .bbox-tag {
  background: #3b82f6;
}

.multi-sub-header {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #1e293b;
  padding: 6px 12px;
  border-bottom: 1px solid #334155;
}

.sub-header-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  white-space: nowrap;
}

.sub-tabs-scroll {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  scrollbar-width: none;
}

.sub-tab-btn {
  background: #0f172a;
  color: #94a3b8;
  border: 1px solid #334155;
  border-radius: 4px;
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.sub-tab-btn:hover {
  background: #334155;
  color: #f8fafc;
}

.sub-tab-btn.active {
  background: #10b981;
  color: white;
  border-color: #059669;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  pointer-events: none;
}

.viewer-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px 20px;
  background: #1e293b;
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid #334155;
  font-size: 0.8rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stat-label {
  color: #94a3b8;
}

.stat-value {
  font-weight: 600;
}

.text-green { color: #4ade80; }
.text-blue { color: #60a5fa; }
.text-sky { color: #38bdf8; }
</style>
