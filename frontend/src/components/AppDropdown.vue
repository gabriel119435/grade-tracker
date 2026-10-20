<script setup>
import {computed, ref} from 'vue'

// custom select: shows a list of options, the picked option's value goes to the parent's v-model
// every option has a value (stored in model, ex: 3) and a label (shown on screen, ex: 'alice')
// options come as objects {value, label} (student selector) or strings (locale picker: value = label = 'en')
// optValue and optLabel read either shape, selectedOption maps the stored value back to its option for the label

const props = defineProps({
  options: {type: Array, required: true},
  // shown when nothing is selected: 'select a student'
  placeholder: {type: String, default: ''},
})
// receives the parent's v-model value, assigning model.value sends it back to the parent: 'en' or 3
const model = defineModel({type: [String, Number]})

// whether the option list is visible
const open = ref(false)
// undefined while nothing valid is selected, shows the gray placeholder
const selectedOption = computed(() => props.options.find((o) => optValue(o) === model.value))

function optValue(o) {
  return typeof o === 'string' ? o : o.value
}

function optLabel(o) {
  return typeof o === 'string' ? o : o.label
}

function select(value) {
  model.value = value
  open.value = false
}

// focus moved to another element outside the dropdown (tab away): close the list
// null target is a click, v-click-outside handles those
function onFocusOut(e) {
  if (e.relatedTarget && !e.currentTarget.contains(e.relatedTarget)) open.value = false
}
</script>

<template>
  <div
    v-click-outside="() => (open = false)"
    class="app-dropdown"
    @keydown.esc="open = false"
    @focusout="onFocusOut"
  >
    <button
      class="app-select-trigger"
      type="button"
      :class="{open}"
      @click="open = !open"
    >
      <!-- :class object syntax: class name -> condition, see FRONT_BASICS.md template syntax -->
      <span :class="{'app-select-placeholder': !selectedOption}">
        {{ selectedOption ? optLabel(selectedOption) : placeholder }}
      </span>
      <span class="app-select-arrow">&#9662;</span>
    </button>
    <div
      v-if="open"
      class="app-select-dropdown"
    >
      <button
        v-for="opt in options"
        :key="optValue(opt)"
        class="app-select-option"
        type="button"
        :class="{active: optValue(opt) === model}"
        @click="select(optValue(opt))"
      >
        {{ optLabel(opt) }}
      </button>
    </div>
  </div>
</template>
