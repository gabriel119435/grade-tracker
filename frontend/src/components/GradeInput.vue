<script setup>
import {computed} from 'vue'

// properties are set by parent, communicated towards children
const props = defineProps({
  modelValue: String, // current input string: '7.5' or ''
  state: {type: String, default: null} // css class applied to wrapper: 'grade-cell-new', 'grade-cell-error' etc., set by parent.
})
// emits are information sent to parent, communicated from children
const emit = defineEmits(['update:modelValue'])

// writable computed so v-model="value" works in the template without mutating the prop directly
const value = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})
</script>

<template>
  <div :class="state" class="grade-input">
    <!-- type="text" prevents the browser from rejecting letters (e.g. "e" for scientific
         notation) before vue sees them, rejection resets cursor to 0 causing a visible jump;
         inputmode="numeric" still shows the numeric keyboard on mobile -->
    <input
        v-model="value"
        inputmode="numeric"
        placeholder="-"
        type="text"
    />
  </div>
</template>
