<script setup>
import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import {useConfirm} from '../composables/generic/useConfirm.js'

const props = defineProps({
  // key in the app-wide pendingId: user id, 'cat-3', 'sub-3', 'seed'
  confirmId: {type: [Number, String], required: true},
  // text before the first click, falls back to common.delete
  label: {type: String, default: null},
  disabled: {type: Boolean, default: false},
})
// fires only on the second click of the same button within 3s
const emit = defineEmits(['confirm'])

const {t} = useI18n()
const {pendingId, confirm} = useConfirm()
const pending = computed(() => pendingId.value === props.confirmId)

function handleClick() {
  if (confirm(props.confirmId)) emit('confirm')
}
</script>

<template>
  <button
    :class="pending ? 'btn-danger-confirm' : 'btn-danger'"
    type="button"
    :disabled="disabled"
    @click="handleClick"
  >
    {{ pending ? t('common.confirmation') : (label ?? t('common.delete')) }}
  </button>
</template>
