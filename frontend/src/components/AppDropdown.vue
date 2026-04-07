<script setup>
import {computed, ref} from 'vue'

const props = defineProps({
  modelValue: [String, Number], // currently selected value: 'en' or 3
  options: Array,               // [{value: 3, label: 'Alice'}] or ['en', 'pt-br']
  placeholder: String,          // shown when nothing is selected: 'select a student'
})

// 'update:modelValue' is vue's convention for plain v-model.
// any parent using v-model="x" on this component automatically listens for this event and writes the emitted value into x, regardless of what x is called.
// the child only knows modelValue; the parent handles the name mapping.
const emit = defineEmits(['update:modelValue'])

function optValue(o) {
  return typeof o === 'string' ? o : o.value
}

function optLabel(o) {
  return typeof o === 'string' ? o : o.label
}

const open = ref(false) // whether the option list is visible
const selectedLabel = computed(() => {
  const opt = props.options.find(o => optValue(o) === props.modelValue)
  return opt ? optLabel(opt) : props.placeholder
})

function select(value) {
  emit('update:modelValue', value)
  open.value = false
}
</script>

<template>
  <div v-click-outside="() => open = false" class="app-dropdown">
    <div :class="{open}" class="app-select-trigger" @click="open = !open">
      <span :class="{'app-select-placeholder': modelValue == null || modelValue === ''}">{{ selectedLabel }}</span>
      <span class="app-select-arrow">▾</span>
    </div>
    <div v-if="open" class="app-select-dropdown">
      <div
          v-for="opt in options"
          :key="optValue(opt)"
          :class="{active: optValue(opt) === modelValue}"
          class="app-select-option"
          @click="select(optValue(opt))"
      >{{ optLabel(opt) }}
      </div>
    </div>
  </div>
</template>
