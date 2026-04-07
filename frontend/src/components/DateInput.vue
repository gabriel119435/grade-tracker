<script setup>
import {computed, ref, watch} from 'vue'
import {useI18n} from 'vue-i18n'
import {localizeDate, validateLocalizedDate} from '../utils/dateUtils.js'

const props = defineProps({
  modelValue: String, // iso date string from parent: '2024-01-31'
})
const emit = defineEmits(['update:modelValue', 'error'])
const {t} = useI18n()

const format = computed(() => t('date_input.format')) // locale date format string: 'DD/MM/YYYY'
const display = ref(localizeDate(props.modelValue, format.value)) // what the user sees in the input: '31/01/2024'
const hasError = ref(false) // true while the typed string is non-empty and not yet a valid date
// computed so the message re-translates automatically when locale changes
const error = computed(() => hasError.value ? t('date_input.invalid') : null) // translated error string or null

// watch(source, callback) runs callback whenever source changes
// source can be a ref (watch(myRef, ...)) or a getter function (watch(() => props.x, ...))
// a getter is needed for props because passing props.x directly gives vue a plain string, not a live reference
// callback receives (newValue, oldValue); oldValue can be omitted if not needed
watch(() => props.modelValue, (val) => {
  const localized = localizeDate(val, format.value)
  if (localized !== display.value) {
    display.value = localized
    hasError.value = false
  }
})

watch(format, () => {
  display.value = localizeDate(props.modelValue, format.value)
})

function onInput(e) {
  display.value = e.target.value
  const normalizedDate = validateLocalizedDate(display.value, format.value)
  if (normalizedDate) {
    hasError.value = false
    emit('error', null)
    emit('update:modelValue', normalizedDate)
  } else {
    hasError.value = display.value.length > 0  // show error as soon as anything is typed
    emit('error', true) // always true when invalid: parent only uses this as a truthy disable signal
  }
}
</script>

<template>
  <input
      :placeholder="format"
      :value="display"
      @input="onInput"
  />
  <span v-if="error" class="date-input-error">{{ error }}</span>
</template>
