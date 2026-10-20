import {getGrades} from '../../api/routes/grades.js'
import {useLoad} from '../generic/useLoad.js'

export function useChartGrades() {
    // chartGrades, last n per subcategory: [{category: 'serve', subcategories: [{id: 3, name: 'slice', grades: []}]}]
    const {data: chartGrades, ready: chartGradesReady, failed: chartGradesFailed, load} = useLoad(getGrades, [])

    // chart data shared by the student and teacher grades views
    // loadChartGrades(studentId, limit) fetches and stores, same values again to retry, see useLoad.js
    // read chartGrades, chartGradesReady and chartGradesFailed, write via loadChartGrades()
    return {chartGrades, chartGradesReady, chartGradesFailed, loadChartGrades: load}
}
