<script setup>
// defineModel is a vue macro that replaces these three parts:
//   1: accept the parent's prop: const props = defineProps({modelValue: String})
//   2: declare the event: const emit = defineEmits(['update:modelValue'])
//   3: the stand-in: reading gives the prop, assigning sends the event
//      const model = computed({get: () => props.modelValue, set: (v) => emit('update:modelValue', v)})
const model = defineModel({type: String})

defineProps({
  state: {type: String, default: null} // css class applied to wrapper: 'grade-cell-new', 'grade-cell-error' etc., set by parent.
})
</script>

<template>
  <div :class="state" class="grade-input">
    <!-- type="text" prevents the browser from rejecting letters (e.g. "e" for scientific
         notation) before vue sees them, rejection resets cursor to 0 causing a visible jump;
         inputmode="decimal" still shows a number keypad on mobile, with a decimal separator key -->
    <input
        v-model="model"
        inputmode="decimal"
        placeholder="-"
        type="text"
    />
  </div>
</template>
