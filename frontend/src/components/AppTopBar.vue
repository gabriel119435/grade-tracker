<script setup>
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {logout, setLocale} from '../api/routes/auth.js'
import {store} from '../store.js'
import {useLoading} from '../composables/generic/useLoading.js'
import {useToast} from '../composables/generic/useToast.js'
import {useAction} from '../composables/generic/useAction.js'
import {translateError} from '../utils/translateError.js'
import {DEFAULT_LOCALE, LOCALES} from '../constants.js'
import AppDropdown from './AppDropdown.vue'

const router = useRouter()
const {t, locale} = useI18n()
const {loading, withLoading} = useLoading()
const {toast} = useToast()
const {runAction} = useAction(withLoading)

// switches the language right away, reverts it if the server rejects the change
async function handleLocaleChange(newLocale) {
  const previous = locale.value
  locale.value = newLocale
  const data = await setLocale(newLocale)
  if (data.error) {
    locale.value = previous
    toast(translateError(data.error), 'error')
  }
}

// the session cookie is httponly, only the server can clear it: on failure stay logged in and say so
async function handleLogout() {
  await runAction(logout, async () => {
    store.user = null
    store.sessionLoaded = false
    locale.value = DEFAULT_LOCALE
    await router.push('/login')
  })
}
</script>

<template>
  <nav class="top-bar">
    <span class="top-bar-left">{{ store.user?.username }}</span>
    <div class="top-bar-center">
      <slot/>
    </div>
    <div class="top-bar-right">
      <!-- v-model split in two: a change must go through handleLocaleChange, which saves it and can revert it -->
      <AppDropdown
        class="app-select-compact"
        :model-value="locale"
        :options="LOCALES"
        @update:model-value="handleLocaleChange"
      />
      <button
        class="btn-danger"
        type="button"
        :disabled="loading"
        @click="handleLogout"
      >
        {{ t('nav.logout') }}
      </button>
    </div>
  </nav>
</template>
