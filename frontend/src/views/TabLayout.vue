<script setup>
import {useI18n} from 'vue-i18n'
import AppToast from '../components/AppToast.vue'
import AppTopBar from '../components/AppTopBar.vue'

const {t} = useI18n()
</script>

<template>
  <div>
    <AppTopBar>
      <div class="top-bar-links">
        <RouterLink to="/teacher/categories">{{ t('nav.categories') }}</RouterLink>
        <RouterLink to="/teacher/students">{{ t('nav.students') }}</RouterLink>
        <RouterLink to="/teacher/grades">{{ t('nav.grades') }}</RouterLink>
      </div>
    </AppTopBar>
    <RouterView/>
    <AppToast/>
  </div>
</template>
