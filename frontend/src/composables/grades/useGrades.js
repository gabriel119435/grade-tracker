import {computed, ref, watch} from 'vue'
import {saveGrades} from '../../api/routes/grades.js'
import {useGradesLoader} from './useGradesLoader.js'
import {localizeGrade, parseGrade, buildGradesIndex, classifyGradeEdits} from '../../utils/gradeUtils.js'
import {localToday} from '../../utils/dateUtils.js'

// categories: reactive list of categories with their subcategories
// ref([{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice'}]}])
// getSeparator: returns the current locale decimal separator: ',' or '.'
export function useGrades(categories, getSeparator) {
    const {loadGrades} = useGradesLoader()
    const inputGradeDate = ref(localToday()) // currently selected date in the date picker: '2024-01-31'
    const inputGradeEdits = ref({}) // {3: '7,5', 4: '', 7: 'abc'} subcategoryId:cell text exactly as shown
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
    }

    async function loadStudentGrades(studentId, resetDate = true, limit = null) {
        const data = await loadGrades(studentId, limit)
        if (!data) return
        indexedGrades.value = buildGradesIndex(data)
        apiResponseGrades.value = data
        if (resetDate) inputGradeDate.value = localToday()
        prefillFromDate(inputGradeDate.value)
    }

    // {3: null, 4: 'grade-cell-new', 7: 'grade-cell-error'}
    const cellStates = computed(() => {
        const dayGrades = indexedGrades.value[inputGradeDate.value] ?? {}
        const result = {}
        for (const {subcategoryId, state} of classifyGradeEdits(dayGrades, inputGradeEdits.value, getSeparator())) {
            result[subcategoryId] = state === 'unchanged' ? null : `grade-cell-${state}`
        }
        return result
    })

    async function submitStudentGrades(studentId) {
        const dayGrades = indexedGrades.value[inputGradeDate.value] ?? {}
        const toUpsert = []
        const toDelete = []

        for (const {subcategoryId, original, value, state} of classifyGradeEdits(dayGrades, inputGradeEdits.value, getSeparator())) {
            if (state === 'new' || state === 'updating') {
                toUpsert.push({
                    subcategory_id: Number(subcategoryId),
                    value
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

    // locale switch: valid cells are rewritten with the new separator, invalid cells are kept as typed
    // en -> pt-br: '7.5' -> '7,5', '' -> '', 'abc' -> 'abc', '5,3' -> '5,3' (now valid)
    watch(getSeparator, (newSeparator, oldSeparator) => {
        for (const [subcategoryId, text] of Object.entries(inputGradeEdits.value)) {
            const {valid, value} = parseGrade(text, oldSeparator)
            if (valid && value !== null) inputGradeEdits.value[subcategoryId] = localizeGrade(value, newSeparator)
        }
    })

    return {
        inputGradeDate,      // ref: currently selected date bound to the date picker
        inputGradeEdits,     // ref: map of subcategoryId:cell text exactly as shown, bound to each GradeInput
        apiResponseGrades,   // ref: raw api response array passed as-is to GradeCharts
        loadStudentGrades,   // async fn(studentId, resetDate?, limit?): fetches grades, rebuilds index, prefills inputs
        submitStudentGrades, // async fn(studentId): diffs inputs vs index, upserts new/changed, deletes cleared
        cellStates           // computed: map of subcategoryId with CSS class string (new/updating/deleting/error/null)
    }
}
