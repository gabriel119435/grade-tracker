<script setup>
import {computed, onMounted, ref, useTemplateRef} from 'vue'
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {getArenas} from '../api/routes/arenas.js'
import {login} from '../api/routes/auth.js'
import {store} from '../store.js'
import {useListLoad} from '../composables/generic/useListLoad.js'
import {useLoading} from '../composables/generic/useLoading.js'
import {translateError} from '../utils/translateError.js'
import {HOME_URL, PASSWORD_MAX_LENGTH, USERNAME_MAX_LENGTH} from '../constants.js'
import AppDropdown from '../components/AppDropdown.vue'
import LoadError from '../components/LoadError.vue'

const router = useRouter()
const {t, locale} = useI18n()
const {items: arenas, failed: arenasFailed, load: loadArenas} = useListLoad(getArenas)
const arenaOptions = computed(() => arenas.value.map((arena) => ({value: arena.id, label: arena.name})))
const arenaId = ref()
const username = ref('')
const password = ref('')
const passwordInput = useTemplateRef('passwordInput')
// shown inline: the login page has no layout, so no AppToast renders here
const error = ref(null)
const {loading, withLoading} = useLoading()

onMounted(loadArenas)

async function handleSubmit() {
  await withLoading(async () => {
    error.value = null
    const data = await login(arenaId.value, username.value, password.value)
    if (data.error) {
      error.value = translateError(data.error)
      passwordInput.value.select()
    } else {
      store.user = data.user
      store.sessionCheckFailed = false
      locale.value = data.user.locale
      await router.push(HOME_URL[data.user.role])
    }
  })
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1>{{ t('login.title') }}</h1>
      <p
        v-if="store.sessionCheckFailed"
        class="field-error"
      >
        {{ t('login.session_check_failed') }}
      </p>
      <form @submit.prevent="handleSubmit">
        <LoadError
          v-if="arenasFailed"
          :message="t('login.arenas_failed')"
          @retry="loadArenas"
        />
        <AppDropdown
          v-else
          v-model="arenaId"
          :options="arenaOptions"
          :placeholder="t('login.arena')"
        />
        <input
          v-model="username"
          type="text"
          required
          :placeholder="t('login.username')"
          :maxlength="USERNAME_MAX_LENGTH"
        />
        <input
          ref="passwordInput"
          v-model="password"
          type="password"
          required
          :placeholder="t('login.password')"
          :maxlength="PASSWORD_MAX_LENGTH"
        />
        <button
          class="btn-primary"
          type="submit"
          :disabled="loading || !arenaId"
        >
          {{ t('login.submit') }}
        </button>
        <p
          v-if="error"
          class="field-error"
        >
          {{ error }}
        </p>
      </form>
    </div>
  </div>
</template>
