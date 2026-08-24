<template>
  <div class="preservation-control-card">
    <div class="control-section">
      <div class="section-header">
        <label class="section-title">Ink Mode</label>
        <span class="mode-badge">{{ inkMode.toUpperCase() }}</span>
      </div>
      <div class="button-group">
        <button 
          class="btn-mode" 
          :class="{ active: inkMode === 'blue' }" 
          @click="updateInkMode('blue')"
        >
          🔵 Blue Ink
        </button>
        <button 
          class="btn-mode" 
          :class="{ active: inkMode === 'black' }" 
          @click="updateInkMode('black')"
        >
          ⚫ Black Ink
        </button>
        <button 
          class="btn-mode" 
          :class="{ active: inkMode === 'auto' }" 
          @click="updateInkMode('auto')"
        >
          ✨ Auto Detect
        </button>
      </div>
    </div>

    <div class="control-section">
      <div class="section-header">
        <label class="section-title">Preservation Sensitivity</label>
        <span class="level-value">{{ Math.round(preservationLevel * 100) }}%</span>
      </div>
      <div class="slider-wrapper">
        <span class="slider-label">Low</span>
        <input 
          type="range" 
          min="0.0" 
          max="1.0" 
          step="0.05"
          :value="preservationLevel"
          @input="onSliderInput"
          class="preservation-slider"
        />
        <span class="slider-label">High</span>
      </div>
      <p class="control-help">
        Higher settings retain faint pressure strokes and micro-tails. Lower settings prioritize aggressive background cleaning.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  inkMode: 'blue' | 'black' | 'auto';
  preservationLevel: number;
}>();

const emit = defineEmits<{
  (e: 'update:inkMode', value: 'blue' | 'black' | 'auto'): void;
  (e: 'update:preservationLevel', value: number): void;
  (e: 'change'): void;
}>();

let debounceTimer: any = null;

function updateInkMode(mode: 'blue' | 'black' | 'auto') {
  emit('update:inkMode', mode);
  triggerChangeDebounced();
}

function onSliderInput(event: Event) {
  const val = parseFloat((event.target as HTMLInputElement).value);
  emit('update:preservationLevel', val);
  triggerChangeDebounced();
}

function triggerChangeDebounced() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    emit('change');
  }, 350);
}
</script>

<style scoped>
.preservation-control-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #cbd5e1;
}

.mode-badge {
  font-size: 0.65rem;
  font-weight: 700;
  background: #3b82f620;
  color: #60a5fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.level-value {
  font-size: 0.8rem;
  font-weight: 700;
  color: #38bdf8;
}

.mode-badge.green {
  background: #10b98120;
  color: #34d399;
}

.button-group {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 4px;
}

.button-group.two-col {
  grid-template-columns: 1fr 1fr;
}

.btn-mode {
  background: #0f172a;
  color: #94a3b8;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 6px 3px;
  font-size: 0.72rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.btn-mode:hover {
  background: #334155;
  color: #f8fafc;
}

.btn-mode.active {
  background: #2563eb;
  color: white;
  border-color: #3b82f6;
}

.slider-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slider-label {
  font-size: 0.7rem;
  color: #94a3b8;
}

.preservation-slider {
  flex: 1;
  accent-color: #38bdf8;
  cursor: pointer;
}

.control-help {
  margin: 0;
  font-size: 0.7rem;
  color: #64748b;
  line-height: 1.25;
}
</style>
