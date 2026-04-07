import {computed, ref, watch} from 'vue'
import {saveGrades} from '../../api/routes/grades.js'
import {useGradesLoader} from './useGradesLoader.js'
import {normalizeGrade, localizeGrade, trunc1dp, validateNormalizedGrade, buildGradesIndex, classifyGradeEdits} from '../../utils/gradeUtils.js'

// categories: reactive list of categories with their subcategories
// ref([{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice'}]}])
// getSeparator: callback so locale changes mid-session are picked up on every keystroke
export function useGrades(categories, getSeparator) {
    const {loadGrades} = useGradesLoader()
    const today = new Date().toISOString().split('T')[0] // '2024-01-31'
    const inputGradeDate = ref(today) // currently selected date in the date picker: '2024-01-31'
    const inputGradeEdits = ref({}) // {3: '7.5', 4: ''} subcategoryId:what the user typed
    const inputGradeErrors = ref({}) // {3: false, 4: true} subcategoryId:true if input is invalid
    // {'2024-01-31': {3: {id: 10, value: 7.5}}} -- loaded grades keyed by date then subcategoryId for O(1) lookup
    const indexedGrades = ref({})
    // raw api response array
    // [{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice', grades: [{id: 10, date: '2024-01-31', value: 7.5}]}]}]
    const apiResponseGrades = ref([])

    function prefillFromDate(date) {
        const dayGrades = indexedGrades.value[date] ?? {}
        const localizedInputs = {}
        for (const cat of categories.value) {
            for (const sub of cat.subcategories) {
                localizedInputs[sub.id] = dayGrades[sub.id] !== undefined ? localizeGrade(dayGrades[sub.id].value, getSeparator()) : ''
            }
        }
        inputGradeEdits.value = localizedInputs
        inputGradeErrors.value = {}
    }

    async function loadStudentGrades(studentId, resetDate = true, limit = null) {
        const data = await loadGrades(studentId, limit)
        if (!data) return
        indexedGrades.value = buildGradesIndex(data)
        apiResponseGrades.value = data
        if (resetDate) inputGradeDate.value = today
        prefillFromDate(inputGradeDate.value)
    }

    // validates one input on keystroke and writes the boolean into inputGradeErrors
    function validateGradeInput(subcategoryId) {
        inputGradeErrors.value[subcategoryId] =
            !validateNormalizedGrade(normalizeGrade(inputGradeEdits.value[subcategoryId], getSeparator()))
    }

    const cellStates = computed(() => {
        const dayGrades = indexedGrades.value[inputGradeDate.value] ?? {}
        const result = {}
        for (const {subcategoryId, state} of classifyGradeEdits(dayGrades, inputGradeEdits.value, getSeparator())) {
            if (inputGradeErrors.value[subcategoryId]) result[subcategoryId] = 'grade-cell-error'
            else result[subcategoryId] = state === 'unchanged' ? null : `grade-cell-${state}`
        }
        return result
    })

    async function submitStudentGrades(studentId) {
        const dayGrades = indexedGrades.value[inputGradeDate.value] ?? {}
        const toUpsert = []
        const toDelete = []

        for (const {subcategoryId, original, normalized, state} of classifyGradeEdits(dayGrades, inputGradeEdits.value, getSeparator())) {
            if (state === 'new' || state === 'updating') {
                toUpsert.push({
                    subcategory_id: Number(subcategoryId),
                    value: trunc1dp(parseFloat(normalized))
                })
            } else if (state === 'deleting') {
                toDelete.push(original.id)
            }
        }

        // short-circuit before calling api
        if (toUpsert.length === 0 && toDelete.length === 0) {
            return {upserted: 0, deleted: 0}
        }

        const data = await saveGrades(studentId, inputGradeDate.value, toUpsert, toDelete)
        if (data.error) return {error: data.error}

        return {upserted: toUpsert.length, deleted: toDelete.length}
    }

    watch(inputGradeDate, prefillFromDate)

    return {
        inputGradeDate,      // ref: currently selected date bound to the date picker
        inputGradeEdits,     // ref: map of subcategoryId:raw locale-formatted string, bound to each GradeInput
        inputGradeErrors,    // ref: map of subcategoryId:true if invalid, false if valid
        apiResponseGrades,   // ref: raw api response array passed as-is to GradeCharts
        loadStudentGrades,   // async fn(studentId, resetDate?, limit?): fetches grades, rebuilds index, prefills inputs
        submitStudentGrades, // async fn(studentId): diffs inputs vs index, upserts new/changed, deletes cleared
        validateGradeInput,  // fn(subcategoryId): validates one input on change using composable-level separator
        cellStates           // computed: map of subcategoryId with CSS class string (new/updating/deleting/error/null)
    }
}
