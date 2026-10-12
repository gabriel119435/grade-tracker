import {computed, ref, watch} from 'vue'
import {getDayGrades, saveGrades} from '../../api/routes/grades.js'
import {useToast} from '../generic/useToast.js'
import {useLatestCall} from '../generic/useLatestCall.js'
import {translateError} from '../../utils/translateError.js'
import {classifyGradeEdits, localizeGrade, parseGrade} from '../../utils/gradeUtils.js'
import {localToday} from '../../utils/dateUtils.js'

// categories: reactive list of categories with their subcategories
// ref([{id: 1, name: 'serve', subcategories: [{id: 3, name: 'slice'}]}])
// getSeparator: returns the current locale decimal separator: ',' or '.'
export function useGrades(categories, getSeparator) {
    const {toast} = useToast()

    // student whose grades are loaded
    const studentId = ref(null)

    // currently selected date in the date picker: '2024-01-31'
    const inputGradeDate = ref(localToday())

    // subcategoryId -> cell text exactly as shown: {3: '7,5', 4: '', 7: 'abc'}
    const cellTexts = ref({})

    // every grade of studentId on inputGradeDate, unlimited: {3: {id: 10, value: 7.5}} keyed by subcategoryId
    // source for prefill, cell states and save
    const savedDayGrades = ref({})

    // drops day loads replaced by a newer student or date pick, see useLatestCall.js
    const {start: startDayLoad} = useLatestCall()

    // true when the newest day load failed, the form shows an inline message instead of the cells
    const savedDayGradesFailed = ref(false)

    // true only after the newest day load succeeded, false before a load, while one is in flight and after a failure
    // every student or date change starts a load, so true always means the current pair, save waits for it
    const savedDayGradesReady = ref(false)

    // every cell classified against the saved grades: error | new | updating | deleting | unchanged
    const classifiedCells = computed(() =>
        classifyGradeEdits(savedDayGrades.value, cellTexts.value, getSeparator())
    )

    // {3: null, 4: 'grade-cell-new', 7: 'grade-cell-error'}
    const cellStates = computed(() => {
        const result = {}
        for (const {subcategoryId, state} of classifiedCells.value) {
            result[subcategoryId] = state === 'unchanged' ? null : `grade-cell-${state}`
        }
        return result
    })

    // true if any cell holds invalid text, blocks save
    const hasGradeErrors = computed(() => classifiedCells.value.some(edit => edit.state === 'error'))

    // true if any valid cell differs from its saved grade, save needs at least one
    const hasChanges = computed(() =>
        classifiedCells.value.some(edit => ['new', 'updating', 'deleting'].includes(edit.state))
    )

    function prefill() {
        const localizedInputs = {}
        for (const cat of categories.value) {
            for (const sub of cat.subcategories) {
                const grade = savedDayGrades.value[sub.id]
                localizedInputs[sub.id] = grade !== undefined ? localizeGrade(grade.value, getSeparator()) : ''
            }
        }
        cellTexts.value = localizedInputs
    }

    async function loadDayGrades() {
        const isLatest = startDayLoad()
        savedDayGradesFailed.value = false
        savedDayGradesReady.value = false
        const data = await getDayGrades(studentId.value, inputGradeDate.value)
        if (!isLatest()) return
        if (data.error) {
            cellTexts.value = {}
            savedDayGrades.value = {}
            savedDayGradesFailed.value = true
            toast(translateError(data.error), 'error')
            return
        }
        savedDayGrades.value = data
        savedDayGradesReady.value = true
        prefill()
    }

    // grade cells of one student, the selected date is kept
    async function loadStudentDayGrades(newStudentId) {
        studentId.value = newStudentId
        await loadDayGrades()
    }

    async function submitStudentGrades() {
        const toUpsert = []
        const toDelete = []

        for (const {subcategoryId, original, value, state} of classifiedCells.value) {
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

        const data = await saveGrades(studentId.value, inputGradeDate.value, toUpsert, toDelete)
        if (data.error) return {error: data.error}

        return {upserted: toUpsert.length, deleted: toDelete.length}
    }

    // date changed: load that date's grades, no student yet means nothing to load
    watch(inputGradeDate, () => {
        if (studentId.value) loadDayGrades()
    })

    // locale switch: valid cells are rewritten with the new separator, invalid cells are kept as typed
    // en -> pt-br: '7.5' -> '7,5', '' -> '', 'abc' -> 'abc', '5,3' -> '5,3' (now valid)
    watch(getSeparator, (newSeparator, oldSeparator) => {
        for (const [subcategoryId, text] of Object.entries(cellTexts.value)) {
            const {valid, value} = parseGrade(text, oldSeparator)
            if (valid && value !== null) cellTexts.value[subcategoryId] = localizeGrade(value, newSeparator)
        }
    })

    // returned to the teacher GradesView:
    // studentId (ref): student whose day grades are loaded, null before the first load
    // inputGradeDate (ref): v-model of GradeForm's date
    // cellTexts (ref): what each grade input shows, keyed by subcategory id
    // savedDayGradesReady (ref): true when the cells can show, false while loading or after a failure
    // savedDayGradesFailed (ref): true after a failed load, GradeForm shows the error and the retry button
    // loadStudentDayGrades(studentId): the selected day's grades of that student, prefills the cells
    // submitStudentGrades(): saves the changed cells, returns {upserted, deleted} or {error}
    // cellStates (computed): css class per cell, new | updating | deleting | error | null
    // hasGradeErrors (computed): true if any cell is invalid, GradeForm disables save
    // hasChanges (computed): true if any cell would be saved, GradeForm disables save when false
    return {
        studentId,
        inputGradeDate,
        cellTexts,
        savedDayGradesReady,
        savedDayGradesFailed,
        loadStudentDayGrades,
        submitStudentGrades,
        cellStates,
        hasGradeErrors,
        hasChanges,
    }
}
