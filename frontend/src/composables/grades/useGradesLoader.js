import {getGrades} from '../../api/routes/grades.js'
import {useToast} from '../generic/useToast.js'
import {translateError} from '../../utils/translateError.js'

// shared fetch + error guard; returns data on success, null on failure
export function useGradesLoader() {
    const {toast} = useToast()

    async function loadGrades(studentId, limit = null) {
        const data = await getGrades(studentId, limit)
        if (data.error) {
            toast(translateError(data.error), 'error')
            return null
        }
        return data
    }

    return {loadGrades}
}
