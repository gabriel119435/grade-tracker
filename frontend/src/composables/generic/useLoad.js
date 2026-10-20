import {ref} from 'vue'
import {useToast} from './useToast.js'
import {useLatestCall} from './useLatestCall.js'
import {translateError} from '../../utils/translateError.js'

// fetchFn: api function returning data or {error}, ex: getStudents, getGrades
// empty: value data holds before a load and after a failure, ex: [] or {}
export function useLoad(fetchFn, empty) {
    const {toast} = useToast()
    const {start} = useLatestCall()

    const data = ref(empty)
    // true when the newest load failed, the view shows an inline message and a retry button
    const failed = ref(false)
    // true only after the newest load succeeded, false before a load, while one is in flight and after a failure
    const ready = ref(false)

    // returns true only when this call's answer was stored, false on error or when a newer call replaced it
    async function load(...args) {
        const isLatest = start()
        failed.value = false
        ready.value = false
        const result = await fetchFn(...args)
        if (!isLatest()) return false
        if (result.error) {
            data.value = empty
            failed.value = true
            toast(translateError(result.error), 'error')
            return false
        }
        data.value = result
        ready.value = true
        return true
    }

    // latest-wins load shared by lists, charts and day grades
    // load(...args) passes args to fetchFn, call it again to retry or refresh
    // an error becomes a toast, resets data to empty and sets failed
    // an answer replaced by a newer call is dropped, see useLatestCall.js
    // read data, ready and failed, write via load()
    return {data, failed, ready, load}
}
