import {getGrades} from '../../api/routes/grades.js'
import {useToast} from '../generic/useToast.js'
import {translateError} from '../../utils/translateError.js'

// shared fetch + error guard; returns data on success, null on failure
export function useGradesLoader() {
    const {toast} = useToast()
    // number of the newest load that started
    let latestLoad = 0

    async function loadGrades(studentId, limit = null) {
        const currentLoad = ++latestLoad
        const data = await getGrades(studentId, limit)
        // a newer load started: drop this stale answer
        if (currentLoad !== latestLoad) return null
        if (data.error) {
            toast(translateError(data.error), 'error')
            return null
        }
        return data
    }

    return {loadGrades}
}
