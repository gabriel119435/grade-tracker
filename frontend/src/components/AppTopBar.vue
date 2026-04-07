<script setup>
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {logout, setLocale} from '../api/routes/auth.js'
import {store} from '../store.js'
import {useLoading} from '../composables/generic/useLoading.js'
import {useToast} from '../composables/generic/useToast.js'
import {translateError} from '../utils/translateError.js'
import AppDropdown from './AppDropdown.vue'

const router = useRouter()
const {t, locale} = useI18n()
const {loading, withLoading} = useLoading()
const {toast} = useToast()

async function handleLocaleChange(newLocale) {
  const previous = locale.value
  locale.value = newLocale
  const data = await setLocale(newLocale)
  if (data.error) {
    locale.value = previous
    toast(translateError(data.error), 'error')
  }
}

async function handleLogout() {
  await withLoading(async () => {
    await logout()
    store.user = null
    store.sessionLoaded = false
    await router.push('/login')
  })
}
</script>

<template>
  <nav>
    <span class="top-bar-left">{{ store.user?.username }}</span>
    <div class="top-bar-center">
      <slot/>
    </div>
    <div class="top-bar-right">
      <AppDropdown :model-value="locale" :options="store.locales" class="app-select-compact"
                   @update:modelValue="handleLocaleChange"/>
      <button :disabled="loading" class="btn-danger" @click="handleLogout">{{ t('nav.logout') }}</button>
    </div>
  </nav>
</template>
