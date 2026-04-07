<script setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {login} from '../api/routes/auth.js'
import {store} from '../store.js'
import {i18n} from '../i18n.js'
import {useLoading} from '../composables/generic/useLoading.js'
import {translateError} from '../utils/translateError.js'

const router = useRouter()
const {t} = useI18n()
const username = ref('')
const password = ref('')
const error = ref(null)
const {loading, withLoading} = useLoading()

async function handleSubmit() {
  await withLoading(async () => {
    error.value = null
    const data = await login(username.value, password.value)
    if (data.error) {
      error.value = translateError(data.error)
    } else {
      store.user = data.user
      if (data.user?.locale) i18n.global.locale.value = data.user.locale
      await router.push(`/${data.user.role}`)
    }
  })
}
</script>

<template>
  <div class="login-page login-card">
    <h1>{{ t('login.title') }}</h1>
    <form @submit.prevent="handleSubmit">
      <input v-model="username" :placeholder="t('login.username')" maxlength="25" required type="text"/>
      <input v-model="password" :placeholder="t('login.password')" maxlength="25" required type="password"/>
      <button :disabled="loading" class="btn-primary" type="submit">{{ t('login.submit') }}</button>
      <p v-if="error" class="login-error">{{ error }}</p>
    </form>
  </div>
</template>