<template>
  <div class="multi-lab-container">
    <div v-if="!activeResult" class="empty-state">
      <div class="empty-icon">📂</div>
      <h2>Multi-Signature Cell Extractor (v1.2 Lab)</h2>
      <p>Select or drop a document scan to detect signature table cells, filter out signatures outside boxes, and auto-populate cropped signatures into your queue.</p>
    </div>

    <div v-else class="lab-workspace">
      <div class="lab-header">
        <div class="header-info">
          <span class="lab-badge">v1.2 Lab</span>
          <span class="sig-count-badge">Detected {{ crops.length }} Signature Cells</span>
        </div>
        <div class="zoom-bar">
          <button class="btn-sm" @click="zoomScale = Math.max(0.25, zoomScale - 0.15)">-</button>
          <span class="zoom-val">{{ Math.round(zoomScale * 100) }}%</span>
          <button class="btn-sm" @click="zoomScale = Math.min(6.0, zoomScale + 0.15)">+</button>
          <button class="btn-sm" @click="zoomScale = 1.0; panX = 0; panY = 0">Fit</button>
        </div>
      </div>

      <div class="lab-body">
        <!-- Panel 1: Original Document Scan with Interactive Cell Bounding Boxes -->
        <div class="panel doc-panel">
          <div class="panel-badge">Original Document & Box Cell Map</div>
          <div 
            class="viewport light-paper"
            @mousedown="startPan"
            @mousemove="onPan"
            @mouseup="endPan"
            @mouseleave="endPan"
          >
            <div class="image-wrapper" :style="transformStyle">
              <img :src="activeResult.original_base64" alt="Original Document" class="preview-img" @dragstart.prevent />
              
              <!-- Bounding Box Overlays -->
              <div class="bbox-layer">
                <div 
                  v-for="(crop, idx) in crops" 
                  :key="crop.id" 
                  class="bbox-rect"
                  :class="{ active: activeSigIndex === idx }"
                  :style="getBboxStyle(crop.bbox)"
                  @click.stop="activeSigIndex = idx"
                >
                  <span class="bbox-tag">{{ crop.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Panel 2: Cropped Signature Box vs Transparent Output -->
        <div class="panel transparent-panel">
          <!-- Background Toggle & View Mode -->
          <div class="bg-toggle-bar">
            <span class="active-sig-title">Selected: {{ currentCrop ? currentCrop.label : 'Sig #1' }}</span>
            <div class="spacer"></div>
            <span class="bg-label">Background:</span>
            <button class="btn-bg" :class="{ active: currentBg === 'checkerboard' }" @click="currentBg = 'checkerboard'">🏁 Checkerboard</button>
            <button class="btn-bg" :class="{ active: currentBg === 'light' }" @click="currentBg = 'light'">☀️ Light</button>
            <button class="btn-bg" :class="{ active: currentBg === 'dark' }" @click="currentBg = 'dark'">🌙 Dark</button>
          </div>

          <!-- Signature Transparency Canvas -->
          <div class="viewport" :class="currentBg">
            <div class="image-wrapper" :style="transformStyle">
              <img :src="currentCrop ? currentCrop.transparent_base64 : ''" alt="Signature Cell Crop" class="preview-img" @dragstart.prevent />
            </div>
          </div>

          <!-- Footer Metadata -->
          <div v-if="currentCrop" class="lab-footer">
            <div class="stat"><span class="lbl">Preserved Pixels:</span> <span class="val green">{{ currentCrop.preserved_pixels.toLocaleString() }}</span></div>
            <div class="stat"><span class="lbl">Background Removed:</span> <span class="val blue">{{ currentCrop.background_pixels.toLocaleString() }}</span></div>
            <div class="stat"><span class="lbl">Confidence:</span> <span class="val sky">{{ Math.round(currentCrop.confidence * 100) }}%</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  activeResult: any;
}>();

const activeSigIndex = ref<number>(0);
const currentBg = ref<'checkerboard' | 'light' | 'dark'>('checkerboard');
const zoomScale = ref<number>(1.0);
const panX = ref<number>(0);
const panY = ref<number>(0);

const isPanning = ref(false);
const startX = ref(0);
const startY = ref(0);

const crops = computed(() => {
  if (props.activeResult?.all_crops) {
    return props.activeResult.all_crops;
  }
  return props.activeResult?.crops || props.activeResult?.signatures || [];
});

const currentCrop = computed(() => {
  if (props.activeResult?.crop_info) {
    return props.activeResult.crop_info;
  }
  if (crops.value.length === 0) {
    if (props.activeResult?.transparent_base64) {
      return {
        transparent_base64: props.activeResult.transparent_base64,
        preserved_pixels: props.activeResult.metadata?.signature_pixels_preserved || 0,
        background_pixels: props.activeResult.metadata?.background_pixels_removed || 0,
        confidence: props.activeResult.confidence || 0.9,
        label: 'Sig'
      };
    }
    return null;
  }
  const idx = Math.min(activeSigIndex.value, crops.value.length - 1);
  return crops.value[idx];
});

const transformStyle = computed(() => ({
  transform: `translate(${panX.value}px, ${panY.value}px) scale(${zoomScale.value})`,
  transformOrigin: 'center center'
}));

function getBboxStyle(bbox: { x: number; y: number; width: number; height: number }) {
  return {
    left: `${bbox.x}px`,
    top: `${bbox.y}px`,
    width: `${bbox.width}px`,
    height: `${bbox.height}px`
  };
}

function startPan(e: MouseEvent) {
  isPanning.value = true;
  startX.value = e.clientX - panX.value;
  startY.value = e.clientY - panY.value;
}

function onPan(e: MouseEvent) {
  if (!isPanning.value) return;
  panX.value = e.clientX - startX.value;
  panY.value = e.clientY - startY.value;
}

function endPan() {
  isPanning.value = false;
}
</script>

<style scoped>
.multi-lab-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  min-height: 0;
  background-color: #020617;
}

.empty-state {
  margin: auto;
  text-align: center;
  max-width: 460px;
  color: #64748b;
}

.empty-icon {
  font-size: 3.5rem;
  margin-bottom: 12px;
  opacity: 0.7;
}

.empty-state h2 {
  font-size: 1.25rem;
  color: #94a3b8;
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 0.85rem;
  line-height: 1.5;
}

.lab-workspace {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  gap: 8px;
  min-height: 0;
}

.lab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1e293b;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #334155;
  flex-shrink: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.lab-badge {
  background: #8b5cf6;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}

.sig-count-badge {
  color: #38bdf8;
  font-size: 0.8rem;
  font-weight: 600;
}

.zoom-bar {
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-sm {
  background: #0f172a;
  color: #cbd5e1;
  border: 1px solid #334155;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-sm:hover {
  background: #334155;
}

.zoom-val {
  font-size: 0.75rem;
  color: #cbd5e1;
  min-width: 40px;
  text-align: center;
}

.lab-body {
  flex: 1;
  display: flex;
  gap: 12px;
  min-height: 0;
  height: 100%;
}

.panel {
  flex: 1;
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

.viewport {
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

.viewport.light-paper {
  background: #f1f5f9;
}

.viewport.checkerboard {
  background-color: #ffffff;
  background-image: linear-gradient(45deg, #e2e8f0 25%, transparent 25%),
                    linear-gradient(-45deg, #e2e8f0 25%, transparent 25%),
                    linear-gradient(45deg, transparent 75%, #e2e8f0 75%),
                    linear-gradient(-45deg, transparent 75%, #e2e8f0 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}

.viewport.light { background-color: #f8fafc; }
.viewport.dark { background-color: #020617; }

.image-wrapper {
  transition: transform 0.05s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  pointer-events: none;
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

.sub-tabs-header {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #1e293b;
  padding: 6px 12px;
  border-bottom: 1px solid #334155;
  flex-shrink: 0;
}

.sub-tabs-label {
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

.bg-toggle-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: #0f172a;
  border-bottom: 1px solid #334155;
  font-size: 0.78rem;
  flex-shrink: 0;
}

.active-sig-title {
  font-weight: 600;
  color: #cbd5e1;
}

.spacer { flex: 1; }

.bg-label { color: #94a3b8; }

.btn-bg {
  background: #1e293b;
  color: #94a3b8;
  border: 1px solid #334155;
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-bg:hover { background: #334155; color: white; }
.btn-bg.active { background: #2563eb; color: white; border-color: #3b82f6; }

.lab-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #1e293b;
  padding: 6px 12px;
  border-top: 1px solid #334155;
  font-size: 0.78rem;
  flex-shrink: 0;
}

.stat { display: flex; align-items: center; gap: 4px; }
.lbl { color: #94a3b8; }
.val { font-weight: 600; }
.green { color: #4ade80; }
.blue { color: #60a5fa; }
.sky { color: #38bdf8; }
</style>
