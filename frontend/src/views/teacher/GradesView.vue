<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useI18n} from 'vue-i18n'
import {getCategories} from '../../api/routes/categories.js'
import {getStudents} from '../../api/routes/students.js'
import {LIMITS, useLimit} from '../../composables/grades/useLimit.js'
import {useLoading} from '../../composables/generic/useLoading.js'
import {useGrades} from '../../composables/grades/useGrades.js'
import {useToast} from '../../composables/generic/useToast.js'
import {translateError} from '../../utils/translateError.js'
import GradeCharts from '../../components/GradeCharts.vue'
import GradeLimitControls from '../../components/GradeLimitControls.vue'
import GradeForm from '../../components/GradeForm.vue'
import AppDropdown from '../../components/AppDropdown.vue'

const {t} = useI18n()
const students = ref([])
const categories = ref([])
const selectedStudentId = ref('')
const showForm = ref(false)
const {loading, withLoading} = useLoading()
const {toast} = useToast()
const {
  inputGradeDate,
  inputGradeEdits,
  inputGradeErrors,
  apiResponseGrades,
  loadStudentGrades,
  submitStudentGrades,
  validateGradeInput,
  cellStates
} = useGrades(categories, () => t('grade_input.decimal_separator')) // getSeparator() is called at use time so locale changes mid-session are picked up
const {limit, setLimit} = useLimit()
const hasGradeErrors = computed(() => Object.values(inputGradeErrors.value).some(Boolean))
const hasChanges = computed(() => Object.values(cellStates.value).some(s => s && s !== 'grade-cell-error'))
const hasGrades = computed(() => apiResponseGrades.value.some(
    cat => cat.subcategories.some(sub => sub.grades.length > 0))
)

onMounted(async () => {
  const [studentsData, categoriesData] = await Promise.all([getStudents(), getCategories()])
  if (!studentsData.error) students.value = studentsData
  if (!categoriesData.error) categories.value = categoriesData
})

watch(selectedStudentId, async (id) => {
  if (id) {
    setLimit(LIMITS[0])
    await loadStudentGrades(id, true, LIMITS[0])
  }
})

async function handleSetLimit(value) {
  setLimit(value)
  await loadStudentGrades(selectedStudentId.value, false, value)
}

async function handleSubmit() {
  await withLoading(async () => {
    const result = await submitStudentGrades(selectedStudentId.value)

    if (result.error) {
      toast(translateError(result.error), 'error')
      return
    }

    const lines = []
    if (result.upserted > 0) lines.push(t('grades.saved', {n: result.upserted}))
    if (result.deleted > 0) lines.push(t('grades.deleted', {n: result.deleted}))
    toast(lines.join('\n'))

    // reloads after save to keep charts in sync
    await loadStudentGrades(Number(selectedStudentId.value), false, limit.value)
  })
}
</script>

<template>
  <div class="vertical-stack">

    <!-- student selector centered, add/hide toggle pinned to the right -->
    <div class="selector-row">
      <AppDropdown
          v-model="selectedStudentId"
          :options="students.map(s => ({value: s.id, label: s.username}))"
          :placeholder="t('grades.select_student')"
      />
      <button v-if="selectedStudentId" class="btn-ghost" @click="showForm = !showForm">
        {{ showForm ? t('grades.hide_form') : t('grades.add') }}
      </button>
    </div>

    <div v-if="selectedStudentId" class="vertical-stack">
      <GradeForm
          v-if="showForm"
          v-model:inputGradeDate="inputGradeDate"
          :categories="categories"
          :inputGradeEdits="inputGradeEdits"
          :cellStates="cellStates"
          :validateGradeInput="validateGradeInput"
          :loading="loading"
          :hasGradeErrors="hasGradeErrors"
          :hasChanges="hasChanges"
          @submit="handleSubmit"
      />

      <GradeCharts :grades="apiResponseGrades">
        <template v-if="hasGrades" #controls>
          <GradeLimitControls :limit="limit" @set="handleSetLimit"/>
        </template>
      </GradeCharts>
    </div>
  </div>
</template>

