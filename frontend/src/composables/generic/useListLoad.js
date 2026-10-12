import {ref} from 'vue'
import {useToast} from './useToast.js'
import {useLatestCall} from './useLatestCall.js'
import {translateError} from '../../utils/translateError.js'

// fetchFn: api function returning a list or {error}, ex: getStudents
export function useListLoad(fetchFn) {
    const {toast} = useToast()
    const {start} = useLatestCall()

    // last loaded list: [{id: 1, username: 'alice', grade_count: 12}]
    const items = ref([])

    // true when the newest load failed, the view shows an inline message and a retry button instead of the list
    const failed = ref(false)

    async function load() {
        const isLatest = start()
        failed.value = false
        const data = await fetchFn()
        if (!isLatest()) return
        if (data.error) {
            items.value = []
            failed.value = true
            toast(translateError(data.error), 'error')
            return
        }
        items.value = data
    }

    // list state shared by the teachers, students, categories and teacher grades views
    // load() fetches and stores, call it again to retry or to refresh after a change
    // an error becomes a toast, clears the list and sets failed
    // an answer replaced by a newer call is dropped, see useLatestCall.js
    // read items and failed, write via load()
    return {items, failed, load}
}
