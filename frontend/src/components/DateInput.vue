<script setup>
import {computed, ref, watch} from 'vue'
import {useI18n} from 'vue-i18n'
import {localizeDate, validateLocalizedDate} from '../utils/dateUtils.js'

// iso date from the parent: '2024-01-31', the parent only ever sets valid dates
const model = defineModel({type: String})
const emit = defineEmits(['error'])
const {t} = useI18n()

// locale date format: 'DD/MM/YYYY'
const format = computed(() => t('date_input.format'))
// what the user sees in the input: '31/01/2024'
const display = ref(localizeDate(model.value, format.value))
// true while the typed text is non-empty and not a valid date
const hasError = ref(false)
// computed so the message re-translates when the locale changes
const error = computed(() => hasError.value ? t('date_input.invalid') : null)

// parent changed the date: show it in the locale format, a valid date clears the error
// a change typed here comes back through v-model too, the check below skips it
watch(model, (value) => {
  const localized = localizeDate(value, format.value)
  // the input already shows it
  if (localized === display.value) return
  display.value = localized
  hasError.value = false
  emit('error', false)
})

// locale changed the format, only reformats, never erases what was typed
watch(format, (newFormat) => {
  // state a: empty input stays empty
  if (display.value === '') return
  // state b: valid date, same date in the new format
  if (!hasError.value) {
    display.value = localizeDate(model.value, newFormat)
    return
  }
  // state c: invalid text stays as typed, accepted only if valid in the new format
  const normalizedDate = validateLocalizedDate(display.value, newFormat)
  if (normalizedDate) {
    hasError.value = false
    emit('error', false)
    model.value = normalizedDate
  }
})

function onInput(e) {
  display.value = e.target.value
  const normalizedDate = validateLocalizedDate(display.value, format.value)
  if (normalizedDate) {
    hasError.value = false
    emit('error', false)
    model.value = normalizedDate
  } else {
    // the message shows as soon as anything is typed, an empty input only blocks save
    hasError.value = display.value.length > 0
    emit('error', true)
  }
}
</script>

<template>
  <input
    :placeholder="format"
    :value="display"
    @input="onInput"
  />
  <span
    v-if="error"
    class="field-error"
  >
    {{ error }}
  </span>
</template>
