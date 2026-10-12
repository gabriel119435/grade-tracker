<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useI18n} from 'vue-i18n'
import {getCategories} from '../../api/routes/categories.js'
import {getStudents} from '../../api/routes/students.js'
import {useLoading} from '../../composables/generic/useLoading.js'
import {useGrades} from '../../composables/grades/useGrades.js'
import {useChartGrades} from '../../composables/grades/useChartGrades.js'
import {useToast} from '../../composables/generic/useToast.js'
import {useAction} from '../../composables/generic/useAction.js'
import {useListLoad} from '../../composables/generic/useListLoad.js'
import {GRADE_HISTORY_LIMITS} from '../../constants.js'
import GradeCharts from '../../components/GradeCharts.vue'
import GradeForm from '../../components/GradeForm.vue'
import AppDropdown from '../../components/AppDropdown.vue'
import LoadError from '../../components/LoadError.vue'

const {t} = useI18n()
// students: [{id: 1, username: 'alice', grade_count: 12}]
const {items: students, failed: studentsFailed, load: loadStudents} = useListLoad(getStudents)
// categories: [{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice'}]}]
const {items: categories, failed: categoriesFailed, load: loadCategories} = useListLoad(getCategories)

// true when either list failed, the page shows only an inline message and a retry
const listsFailed = computed(() => studentsFailed.value || categoriesFailed.value)

// student id (number) once picked
const selectedStudentId = ref(null)

const showForm = ref(false)
const {loading, withLoading} = useLoading()
const {toast} = useToast()
const {runAction} = useAction(withLoading)
const {
  studentId: dayGradesStudentId,
  inputGradeDate,
  cellTexts,
  savedDayGradesReady,
  savedDayGradesFailed,
  loadStudentDayGrades,
  submitStudentGrades,
  cellStates,
  hasGradeErrors,
  hasChanges,
} = useGrades(categories, () => t('grade_input.decimal_separator'))
const {chartGrades, chartGradesReady, chartGradesFailed, loadChartGrades} = useChartGrades()
const limit = ref(GRADE_HISTORY_LIMITS[0])

// AppDropdown options: [{value: 1, label: 'alice'}]
const studentOptions = computed(() => students.value.map(s => ({value: s.id, label: s.username})))

// both lists are needed: no students means nothing to pick, no categories means a form without cells
function loadLists() {
  return Promise.all([loadStudents(), loadCategories()])
}

onMounted(loadLists)

// charts always, day grades only while the form is open: a hidden form shows no cells
async function loadStudent(id) {
  const loads = [loadChartGrades(id, limit.value)]
  if (showForm.value) loads.push(loadStudentDayGrades(id))
  await Promise.all(loads)
}

async function handleSubmit() {
  await runAction(submitStudentGrades, async (result) => {
    const lines = []
    if (result.upserted > 0) lines.push(t('grades.saved', {n: result.upserted}))
    if (result.deleted > 0) lines.push(t('grades.deleted', {n: result.deleted}))
    toast(lines.join('\n'))

    // reloads after save to keep charts and cells in sync with the backend
    await loadStudent(selectedStudentId.value)
  })
}

watch(selectedStudentId, async (id) => {
  if (id) await loadStudent(id)
})

// limit buttons: charts only, typed grade cells are kept
watch(limit, (value) => loadChartGrades(selectedStudentId.value, value))

// opening the form loads its day grades, unless they already belong to the selected student
watch(showForm, (open) => {
  if (open && dayGradesStudentId.value !== selectedStudentId.value) loadStudentDayGrades(selectedStudentId.value)
})
</script>

<template>
  <LoadError
    v-if="listsFailed"
    class="list-card"
    :message="t('grades.lists_failed')"
    @retry="loadLists"
  />
  <div
    v-else
    class="vertical-stack"
  >
    <div class="selector-row">
      <AppDropdown
        v-model="selectedStudentId"
        :options="studentOptions"
        :placeholder="t('grades.select_student')"
      />
      <button
        v-if="selectedStudentId"
        class="btn-ghost"
        type="button"
        @click="showForm = !showForm"
      >
        {{ showForm ? t('grades.hide_form') : t('grades.add') }}
      </button>
    </div>

    <div
      v-if="selectedStudentId"
      class="vertical-stack"
    >
      <GradeForm
        v-if="showForm"
        v-model:input-grade-date="inputGradeDate"
        :categories="categories"
        :cell-texts="cellTexts"
        :cell-states="cellStates"
        :loading="loading"
        :has-grade-errors="hasGradeErrors"
        :has-changes="hasChanges"
        :saved-day-grades-ready="savedDayGradesReady"
        :saved-day-grades-failed="savedDayGradesFailed"
        @edit="(id, text) => cellTexts[id] = text"
        @submit="handleSubmit"
        @retry="loadStudentDayGrades(selectedStudentId)"
      />

      <GradeCharts
        v-model:limit="limit"
        :grades="chartGrades"
        :ready="chartGradesReady"
        :failed="chartGradesFailed"
        @retry="loadChartGrades(selectedStudentId, limit)"
      />
    </div>
  </div>
</template>
