<script setup>
import {useI18n} from 'vue-i18n'
import {GRADE_HISTORY_LIMITS} from '../constants.js'

const model = defineModel({type: Number})
const {t} = useI18n()
</script>

<template>
  <div class="btn-group">
    <span class="btn-group-label">{{ t('charts.last') }}</span>
    <button
      v-for="n in GRADE_HISTORY_LIMITS"
      :key="n"
      class="btn-group-item"
      type="button"
      :class="{active: model === n}"
      @click="model = n"
    >
      {{ n }}
    </button>
  </div>
</template>
