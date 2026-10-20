<script setup>
import {computed, ref, useTemplateRef} from 'vue'
import {useI18n} from 'vue-i18n'
import {changeAdminPassword} from '../../api/routes/auth.js'
import {createTeacher, deleteTeacher, getTeachers} from '../../api/routes/teachers.js'
import {seedDatabase} from '../../api/routes/seed.js'
import {useLoading} from '../../composables/generic/useLoading.js'
import {useToast} from '../../composables/generic/useToast.js'
import {useAction} from '../../composables/generic/useAction.js'
import {translateError} from '../../utils/translateError.js'
import {isPasswordTooShort} from '../../utils/inputValidation.js'
import {LIMIT_PARAMS, PASSWORD_MAX_LENGTH} from '../../constants.js'
import UserList from '../../components/UserList.vue'
import ConfirmButton from '../../components/ConfirmButton.vue'

const {t} = useI18n()

// api functions handed to UserList
const teacherApi = {get: getTeachers, create: createTeacher, remove: deleteTeacher}

// the UserList instance, its load() refreshes the teacher list after a seed
const userList = useTemplateRef('userList')

const adminOldPassword = ref('')
const adminNewPassword = ref('')

// live input check, shows its .field-error line and disables its submit button
const adminNewPasswordError = computed(() => isPasswordTooShort(adminNewPassword.value))

// shared with UserList: one action at a time across the whole page
const loader = useLoading()
const {loading, withLoading} = loader
const {toast} = useToast()
const {runAction} = useAction(withLoading)

async function handleChangePassword() {
  await runAction(
    () => changeAdminPassword(adminOldPassword.value, adminNewPassword.value),
    () => {
      adminOldPassword.value = ''
      adminNewPassword.value = ''
      toast(t('teachers.password_changed'))
    },
  )
}

async function handleSeed() {
  await runAction(seedDatabase, async (data) => {
    // short placeholders keep seed_done under 120 chars in the locale files
    const counts = {t: data.teachers, s: data.students, c: data.categories, sc: data.subcategories, g: data.grades}
    toast(t('teachers.seed_done', counts))
    await userList.value.load()
  })
}
</script>

<template>
  <div class="vertical-stack">
    <UserList
      ref="userList"
      :api="teacherApi"
      i18n-prefix="teachers"
      :loader="loader"
    />

    <form
      class="single-line-form"
      @submit.prevent="handleChangePassword"
    >
      <input
        v-model="adminOldPassword"
        type="password"
        required
        :placeholder="t('teachers.current_password')"
        :maxlength="PASSWORD_MAX_LENGTH"
      />
      <input
        v-model="adminNewPassword"
        type="password"
        required
        :placeholder="t('teachers.new_password', LIMIT_PARAMS)"
        :maxlength="PASSWORD_MAX_LENGTH"
      />
      <button
        class="btn-primary"
        type="submit"
        :disabled="loading || adminNewPasswordError"
      >
        {{ t('teachers.change_password') }}
      </button>
    </form>
    <span
      v-if="adminNewPasswordError"
      class="field-error"
    >
      {{ translateError('password_too_short') }}
    </span>

    <ConfirmButton
      confirm-id="seed"
      :label="t('teachers.seed')"
      :disabled="loading"
      @confirm="handleSeed"
    />
  </div>
</template>
