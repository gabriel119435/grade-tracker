<script setup>
import {watchEffect} from 'vue'
import {useI18n} from 'vue-i18n'

const {t} = useI18n()
watchEffect(() => {
  document.title = t('app.title')
})
</script>

<template>
  <RouterView/>
</template>
