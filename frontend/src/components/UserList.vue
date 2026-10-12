<script setup>
import {computed, onMounted, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import {useLoading} from '../composables/generic/useLoading.js'
import {useAction} from '../composables/generic/useAction.js'
import {useConfirm} from '../composables/generic/useConfirm.js'
import {useListLoad} from '../composables/generic/useListLoad.js'
import {translateError} from '../utils/translateError.js'
import {hasLeadingOrTrailingSpaces, isNameWordTooLong, isPasswordTooShort} from '../utils/inputValidation.js'
import {PASSWORD_MAX_LENGTH, USERNAME_MAX_LENGTH} from '../constants.js'
import LoadError from './LoadError.vue'

// create form, live checks, list and two-click delete of one user role, shared by TeachersView and StudentsView

const props = defineProps({
  // api functions of the listed role: {get: getStudents, create: createStudent, remove: deleteStudent}
  api: {type: Object, required: true},
  // locale prefix holding create, grade_count and load_failed: 'teachers' or 'students'
  i18nPrefix: {type: String, required: true},
  // optional {loading, withLoading} from the parent's useLoading(): one action at a time across the whole page
  loader: {type: Object, default: null},
})

const {t} = useI18n()

// users: [{id: 1, username: 'alice', grade_count: 12}]
const {items: users, failed: usersFailed, load} = useListLoad(props.api.get)

const username = ref('')
const password = ref('')

// live input checks, each shows its .field-error line and disables the create button
const usernameError = computed(() => hasLeadingOrTrailingSpaces(username.value))
const usernameWordError = computed(() => isNameWordTooLong(username.value))
const passwordError = computed(() => isPasswordTooShort(password.value))

const {loading, withLoading} = props.loader ?? useLoading()
const {runAction} = useAction(withLoading)
const {pendingId, confirm} = useConfirm()

onMounted(load)

async function handleCreate() {
  await runAction(() => props.api.create(username.value, password.value), async () => {
    username.value = ''
    password.value = ''
    await load()
  })
}

async function handleDelete(id) {
  if (!confirm(id)) return
  await runAction(() => props.api.remove(id), load)
}

// TeachersView reloads the list after a seed
defineExpose({load})
</script>

<template>
  <form
    class="single-line-form"
    @submit.prevent="handleCreate"
  >
    <input
      v-model="username"
      required
      :placeholder="t('common.username')"
      :maxlength="USERNAME_MAX_LENGTH"
    />
    <!-- visible on purpose: whoever creates the account reads the password to hand it over -->
    <input
      v-model="password"
      required
      :placeholder="t('common.password')"
      :maxlength="PASSWORD_MAX_LENGTH"
    />
    <button
      class="btn-primary"
      type="submit"
      :disabled="loading || usernameError || usernameWordError || passwordError"
    >
      {{ t(`${i18nPrefix}.create`) }}
    </button>
  </form>
  <span
    v-if="usernameError"
    class="field-error"
  >
    {{ translateError('username_spaces') }}
  </span>
  <span
    v-if="usernameWordError"
    class="field-error"
  >
    {{ translateError('word_too_long') }}
  </span>
  <span
    v-if="passwordError"
    class="field-error"
  >
    {{ translateError('password_too_short') }}
  </span>

  <LoadError
    v-if="usersFailed"
    class="list-card"
    :message="t(`${i18nPrefix}.load_failed`)"
    @retry="load"
  />
  <div
    v-else-if="users.length"
    class="list-card"
  >
    <div
      v-for="user in users"
      :key="user.id"
      class="item-row"
    >
      <div class="user-info">
        <strong class="wrap-name">{{ user.username }}</strong>
        <span class="user-count">{{ t(`${i18nPrefix}.grade_count`, {n: user.grade_count}) }}</span>
      </div>
      <button
        :class="pendingId === user.id ? 'btn-danger-confirm' : 'btn-danger'"
        type="button"
        :disabled="loading"
        @click="handleDelete(user.id)"
      >
        {{ pendingId === user.id ? t('common.confirmation') : t('common.delete') }}
      </button>
    </div>
  </div>
</template>
