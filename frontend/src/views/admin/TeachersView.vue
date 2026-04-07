<script setup>
import {computed, onMounted, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import {changeAdminPassword} from '../../api/routes/auth.js'
import {createTeacher, deleteTeacher, getTeachers} from '../../api/routes/teachers.js'
import {useLoading} from '../../composables/generic/useLoading.js'
import {useToast} from '../../composables/generic/useToast.js'
import {useConfirm} from '../../composables/generic/useConfirm.js'
import {translateError} from '../../utils/translateError.js'
import {hasLeadingOrTrailingSpaces, isTooShort} from '../../utils/credentialValidation.js'

const {t} = useI18n()
const teachers = ref([]) // [{id: 1, username: 'alice', grade_count: 42}]
const teacherUsername = ref('')
const teacherPassword = ref('')
const teacherUsernameError = computed(() => hasLeadingOrTrailingSpaces(teacherUsername.value)) // true if username has leading or trailing spaces
const teacherPasswordError = computed(() => isTooShort(teacherPassword.value)) // true if password is non-empty but under 8 chars
const adminOldPassword = ref('')
const adminNewPassword = ref('')
const {loading, withLoading} = useLoading() // loading true while any request is in flight, withLoading wraps async calls
const {toast} = useToast()
const {pendingId, confirm} = useConfirm() // pendingId is id awaiting confirmation, confirm(id): returns false on first click, true on second

async function load() {
  const data = await getTeachers()
  if (!data.error) teachers.value = data
}

onMounted(load)

async function handleCreateTeacher() {
  await withLoading(async () => {
    const data = await createTeacher(teacherUsername.value, teacherPassword.value)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      teacherUsername.value = ''
      teacherPassword.value = ''
      await load()
    }
  })
}

async function handleDelete(id) {
  if (!confirm(id)) return
  await withLoading(async () => {
    const data = await deleteTeacher(id)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      await load()
    }
  })
}

async function handleChangePassword() {
  await withLoading(async () => {
    const data = await changeAdminPassword(adminOldPassword.value, adminNewPassword.value)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      adminOldPassword.value = ''
      adminNewPassword.value = ''
      toast(t('teachers.password_changed'))
    }
  })
}
</script>

<template>
  <div class="vertical-stack">
    <form class="single-line-form" @submit.prevent="handleCreateTeacher">
      <input v-model="teacherUsername" :placeholder="t('common.username')" maxlength="25" required/>
      <input v-model="teacherPassword" :placeholder="t('common.password')" maxlength="25" required/>
      <button :disabled="loading || teacherUsernameError || teacherPasswordError" class="btn-primary" type="submit">
        {{ t('teachers.create') }}
      </button>
    </form>
    <span v-if="teacherUsernameError" class="field-error">{{ t('common.username_spaces') }}</span>
    <span v-if="teacherPasswordError" class="field-error">{{ t('common.password_too_short') }}</span>
    <div v-if="teachers.length" class="list-card">
      <div v-for="teacher in teachers" :key="teacher.id" class="item-row">
        <div class="user-info">
          <strong>{{ teacher.username }}</strong>
          <span class="user-count">{{ t('teachers.grade_count', {n: teacher.grade_count}) }}</span>
        </div>
        <button :disabled="loading" :class="pendingId === teacher.id ? 'btn-danger-confirm' : 'btn-danger'"
                @click="handleDelete(teacher.id)">
          {{ pendingId === teacher.id ? t('common.confirmation') : t('common.delete') }}
        </button>
      </div>
    </div>

    <form class="single-line-form" @submit.prevent="handleChangePassword">
      <input v-model="adminOldPassword" :placeholder="t('teachers.current_password')" maxlength="25" required type="password"/>
      <input v-model="adminNewPassword" :placeholder="t('teachers.new_password')" maxlength="25" required
             type="password"/>
      <button :disabled="loading" class="btn-primary" type="submit">{{ t('teachers.change_password') }}</button>
    </form>
  </div>
</template>
