<script setup>
import {ref, useTemplateRef} from 'vue'
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {login} from '../api/routes/auth.js'
import {store} from '../store.js'
import {useLoading} from '../composables/generic/useLoading.js'
import {translateError} from '../utils/translateError.js'
import {PASSWORD_MAX_LENGTH, USERNAME_MAX_LENGTH} from '../constants.js'

const router = useRouter()
const {t, locale} = useI18n()
const username = ref('')
const password = ref('')
const passwordInput = useTemplateRef('passwordInput')
// shown inline: the login page has no layout, so no AppToast renders here
const error = ref(null)
const {loading, withLoading} = useLoading()

async function handleSubmit() {
  await withLoading(async () => {
    error.value = null
    const data = await login(username.value, password.value)
    if (data.error) {
      error.value = translateError(data.error)
      passwordInput.value.select()
    } else {
      store.user = data.user
      store.sessionCheckFailed = false
      locale.value = data.user.locale
      await router.push(`/${data.user.role}`)
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
          :disabled="loading"
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
