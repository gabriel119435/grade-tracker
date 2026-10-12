<script setup>
defineProps({
  // css class for the wrapper, from GradeForm's cellStates: 'grade-cell-new', 'grade-cell-error' etc
  state: {type: String, default: null},
})
const model = defineModel({type: String})
</script>

<template>
  <div
    class="grade-input"
    :class="state"
  >
    <!-- inputmode decimal: phones show a number keypad with a decimal separator key -->
    <input
      v-model="model"
      inputmode="decimal"
      maxlength="4"
      placeholder="-"
      type="text"
    />
  </div>
</template>
