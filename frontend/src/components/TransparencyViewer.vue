<template>
  <div class="transparency-viewer">
    <div class="background-toggle-bar">
      <span class="badge-title">Extracted Signature</span>
      <div class="header-spacer"></div>
      <span class="toggle-label">Background:</span>
      <button 
        class="btn-bg-toggle" 
        :class="{ active: currentBg === 'checkerboard' }" 
        @click="currentBg = 'checkerboard'"
      >
        🏁 Checkerboard
      </button>
      <button 
        class="btn-bg-toggle" 
        :class="{ active: currentBg === 'light' }" 
        @click="currentBg = 'light'"
      >
        ☀️ Light
      </button>
      <button 
        class="btn-bg-toggle" 
        :class="{ active: currentBg === 'dark' }" 
        @click="currentBg = 'dark'"
      >
        🌙 Dark
      </button>
    </div>

    <div 
      class="canvas-viewport"
      :class="currentBg"
      ref="viewport"
      @mousedown="startPan"
      @mousemove="onPan"
      @mouseup="endPan"
      @mouseleave="endPan"
      @wheel.prevent="onWheel"
    >
      <div 
        class="image-wrapper"
        :style="transformStyle"
      >
        <img 
          :src="imageSrc" 
          alt="Signature Preview" 
          class="preview-img"
          @dragstart.prevent
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  imageSrc: string;
  zoomScale: number;
  panX: number;
  panY: number;
}>();

const emit = defineEmits<{
  (e: 'update:pan', payload: { x: number; y: number }): void;
  (e: 'update:zoom', value: number): void;
}>();

function onWheel(event: WheelEvent) {
  const delta = event.deltaY < 0 ? 0.15 : -0.15;
  const nextZoom = Math.min(8.0, Math.max(0.25, Number((props.zoomScale + delta).toFixed(2))));
  emit('update:zoom', nextZoom);
}

const currentBg = ref<'checkerboard' | 'light' | 'dark'>('checkerboard');
const isPanning = ref(false);
const startMouseX = ref(0);
const startMouseY = ref(0);
const initialPanX = ref(0);
const initialPanY = ref(0);

const transformStyle = computed(() => ({
  transform: `translate(${props.panX}px, ${props.panY}px) scale(${props.zoomScale})`,
  transformOrigin: 'center center'
}));

function startPan(event: MouseEvent) {
  isPanning.value = true;
  startMouseX.value = event.clientX;
  startMouseY.value = event.clientY;
  initialPanX.value = props.panX;
  initialPanY.value = props.panY;
}

function onPan(event: MouseEvent) {
  if (!isPanning.value) return;
  const dx = event.clientX - startMouseX.value;
  const dy = event.clientY - startMouseY.value;
  emit('update:pan', {
    x: initialPanX.value + dx,
    y: initialPanY.value + dy
  });
}

function endPan() {
  isPanning.value = false;
}
</script>

<style scoped>
.transparency-viewer {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  min-height: 0;
  background: #0f172a;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #334155;
}

.background-toggle-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
  font-size: 0.85rem;
  flex-shrink: 0;
}

.badge-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #f1f5f9;
  background: #020617;
  padding: 3px 10px;
  border-radius: 6px;
  border: 1px solid #334155;
}

.header-spacer {
  flex: 1;
}

.toggle-label {
  color: #94a3b8;
  font-weight: 500;
  margin-right: 4px;
}

.btn-bg-toggle {
  background: #0f172a;
  color: #cbd5e1;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-bg-toggle:hover {
  background: #334155;
}

.btn-bg-toggle.active {
  background: #2563eb;
  color: white;
  border-color: #3b82f6;
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

.canvas-viewport:active {
  cursor: grabbing;
}

.canvas-viewport.checkerboard {
  background-color: #ffffff;
  background-image: linear-gradient(45deg, #e2e8f0 25%, transparent 25%),
                    linear-gradient(-45deg, #e2e8f0 25%, transparent 25%),
                    linear-gradient(45deg, transparent 75%, #e2e8f0 75%),
                    linear-gradient(-45deg, transparent 75%, #e2e8f0 75%);
  background-size: 20px 20px;
  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
}

.canvas-viewport.light {
  background-color: #f8fafc;
}

.canvas-viewport.dark {
  background-color: #020617;
}

.image-wrapper {
  transition: transform 0.05s ease-out;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  pointer-events: none;
}
</style>
