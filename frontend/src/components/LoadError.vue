<script setup>
import {useI18n} from 'vue-i18n'

// shown in place of data that failed to load, inside the same card the data would fill
// the caller passes that card class, vue adds it to the root div: <LoadError class="list-card" .../>
// retry vanishes on click: the caller's load resets its failed flag first
defineProps({
  message: {type: String, required: true},
})
const emit = defineEmits(['retry'])
const {t} = useI18n()
</script>

<template>
  <div class="load-error">
    <p class="field-error">{{ message }}</p>
    <button
      class="btn-primary"
      type="button"
      @click="emit('retry')"
    >
      {{ t('common.retry') }}
    </button>
  </div>
</template>
