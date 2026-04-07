<script setup>
import {useI18n} from 'vue-i18n'
import {LIMITS} from '../composables/grades/useLimit.js'

const {t} = useI18n()
defineProps({limit: Number})
const emit = defineEmits(['set']) // parent listens with @set="someHandler" and receives n as the argument
</script>

<template>
  <div class="btn-group">
    <span class="btn-group-label">{{ t('charts.last') }}</span>
    <button
        v-for="n in LIMITS"
        :key="n"
        :class="['btn-group-item', {active: limit === n}]"
        @click="emit('set', n)"
    >{{ n }}
    </button>
  </div>
</template>
