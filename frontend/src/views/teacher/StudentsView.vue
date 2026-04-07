<script setup>
import {computed, onMounted, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import {createStudent, deleteStudent, getStudents} from '../../api/routes/students.js'
import {useLoading} from '../../composables/generic/useLoading.js'
import {useToast} from '../../composables/generic/useToast.js'
import {useConfirm} from '../../composables/generic/useConfirm.js'
import {translateError} from '../../utils/translateError.js'
import {hasLeadingOrTrailingSpaces, isTooShort} from '../../utils/credentialValidation.js'

async function load() {
  const data = await getStudents()
  if (!data.error) students.value = data
}

const {t} = useI18n()
const students = ref([]) // [{id: 1, username: 'alice', grade_count: 12}]
const newUsername = ref('')
const newPassword = ref('')
const usernameError = computed(() => hasLeadingOrTrailingSpaces(newUsername.value)) // true if username has leading or trailing spaces
const passwordError = computed(() => isTooShort(newPassword.value)) // true if password is non-empty but under 8 chars
const {loading, withLoading} = useLoading()
const {toast} = useToast()
const {pendingId, confirm} = useConfirm()

onMounted(load)

async function handleDelete(id) {
  if (!confirm(id)) return
  await withLoading(async () => {
    const data = await deleteStudent(id)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      await load()
    }
  })
}

async function handleCreateStudent() {
  await withLoading(async () => {
    const data = await createStudent(newUsername.value, newPassword.value)
    if (data.error) {
      toast(translateError(data.error), 'error')
    } else {
      newUsername.value = ''
      newPassword.value = ''
      await load()
    }
  })
}
</script>

<template>
  <div class="vertical-stack">
    <form class="single-line-form" @submit.prevent="handleCreateStudent">
      <input v-model="newUsername" :placeholder="t('common.username')" maxlength="25" required/>
      <input v-model="newPassword" :placeholder="t('common.password')" maxlength="25" required/>
      <button :disabled="loading || usernameError || passwordError" class="btn-primary" type="submit">
        {{ t('students.create') }}
      </button>
    </form>
    <span v-if="usernameError" class="field-error">{{ t('common.username_spaces') }}</span>
    <span v-if="passwordError" class="field-error">{{ t('common.password_too_short') }}</span>
    <div v-if="students.length" class="list-card">
      <div v-for="student in students" :key="student.id" class="item-row">
        <div class="user-info">
          <strong>{{ student.username }}</strong>
          <span class="user-count">{{ t('students.grade_count', {n: student.grade_count}) }}</span>
        </div>
        <button :disabled="loading" :class="pendingId === student.id ? 'btn-danger-confirm' : 'btn-danger'"
                @click="handleDelete(student.id)">
          {{ pendingId === student.id ? t('common.confirmation') : t('common.delete') }}
        </button>
      </div>
    </div>
  </div>
</template>
