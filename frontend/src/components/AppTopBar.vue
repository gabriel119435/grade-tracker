<script setup>
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {logout, setLocale} from '../api/routes/auth.js'
import {clearSession, store} from '../store.js'
import {useLoading} from '../composables/generic/useLoading.js'
import {useToast} from '../composables/generic/useToast.js'
import {useAction} from '../composables/generic/useAction.js'
import {translateError} from '../utils/translateError.js'
import {LOCALES} from '../constants.js'
import AppDropdown from './AppDropdown.vue'

const router = useRouter()
const {t, locale} = useI18n()
const {loading, withLoading} = useLoading()
const {toast} = useToast()
const {runAction} = useAction(withLoading)

// switches the language right away, reverts it if the server rejects the change
// withLoading ignores another pick until the server answers, so each revert targets the last saved language
async function handleLocaleChange(newLocale) {
  await withLoading(async () => {
    const previous = locale.value
    locale.value = newLocale
    const data = await setLocale(newLocale)
    if (data.error) {
      locale.value = previous
      toast(translateError(data.error), 'error')
    }
  })
}

// the session cookie is httponly, only the server can clear it: on failure stay logged in and say so
async function handleLogout() {
  await runAction(logout, async () => {
    clearSession()
    await router.push('/login')
  })
}
</script>

<template>
  <nav class="top-bar">
    <!-- left: arena and locale, the context of the session -->
    <div class="top-bar-left">
      <span class="top-bar-pill top-bar-arena">{{ store.user?.arena_name }}</span>
      <!-- v-model split in two: a change must go through handleLocaleChange, which saves it and can revert it -->
      <AppDropdown
        class="app-select-compact top-bar-locale"
        :model-value="locale"
        :options="LOCALES"
        @update:model-value="handleLocaleChange"
      />
    </div>
    <div class="top-bar-center">
      <slot />
    </div>
    <!-- right: the logged-in user and the logout acting on it -->
    <div class="top-bar-right">
      <span class="top-bar-pill top-bar-user">{{ store.user?.username }}</span>
      <button
        class="btn-danger top-bar-logout"
        type="button"
        :disabled="loading"
        @click="handleLogout"
      >
        {{ t('nav.logout') }}
      </button>
    </div>
  </nav>
</template>
