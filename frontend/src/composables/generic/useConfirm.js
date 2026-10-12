import {ref} from 'vue'

const CONFIRM_TIMEOUT_MS = 3000

const pendingId = ref(null)
let timer = null

export function useConfirm() {
    function confirm(id) {
        if (pendingId.value === id) {
            clearTimeout(timer)
            pendingId.value = null
            return true
        }
        clearTimeout(timer)
        pendingId.value = id
        timer = setTimeout(() => {
            pendingId.value = null
        }, CONFIRM_TIMEOUT_MS)
        return false
    }

    // destructive actions (delete, seed) need two clicks on the same button, so a misclick does nothing
    // single pendingId for the whole app, one button pending at a time, cleared after 3s
    // confirm(id) false on first click, true on second click of same id (user_id, 'cat-3', 'sub-3', 'seed')
    // read `pendingId` to show the confirm style, write via `confirm()`
    return {pendingId, confirm}
}
