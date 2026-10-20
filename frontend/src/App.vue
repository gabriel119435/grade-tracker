<script setup>
import {watchEffect} from 'vue'
import {useI18n} from 'vue-i18n'

const {t, locale} = useI18n()
watchEffect(() => {
  document.title = t('app.title')
  // used by screen readers and browser translation
  document.documentElement.lang = locale.value
})
</script>

<template>
  <RouterView />
</template>
