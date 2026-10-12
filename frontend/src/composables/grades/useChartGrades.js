import {ref} from 'vue'
import {getGrades} from '../../api/routes/grades.js'
import {useToast} from '../generic/useToast.js'
import {useLatestCall} from '../generic/useLatestCall.js'
import {translateError} from '../../utils/translateError.js'

export function useChartGrades() {
    const {toast} = useToast()
    const {start} = useLatestCall()

    // last n grades per subcategory: [{category: 'serve', subcategories: [{id: 3, name: 'slice', grades: [...]}]}]
    const chartGrades = ref([])

    // true when the newest chart load failed, GradeCharts shows an inline error message and a retry button
    const chartGradesFailed = ref(false)

    // true only after the newest load succeeded, false before a load, while one is in flight and after a failure
    const chartGradesReady = ref(false)

    async function loadChartGrades(studentId, limit) {
        const isLatest = start()
        chartGradesFailed.value = false
        chartGradesReady.value = false
        const data = await getGrades(studentId, limit)
        if (!isLatest()) return
        if (data.error) {
            chartGrades.value = []
            chartGradesFailed.value = true
            toast(translateError(data.error), 'error')
            return
        }
        chartGrades.value = data
        chartGradesReady.value = true
    }

    // chart data shared by the student and teacher grades views
    // loadChartGrades(studentId, limit) fetches and stores, call it again with the same values to retry
    // an error becomes a toast, clears the charts and sets chartGradesFailed
    // an answer replaced by a newer call is dropped, see useLatestCall.js
    // read chartGrades, chartGradesReady and chartGradesFailed, write via loadChartGrades()
    return {chartGrades, chartGradesReady, chartGradesFailed, loadChartGrades}
}
