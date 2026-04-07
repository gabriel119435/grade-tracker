import {ref} from 'vue'

const CONFIRM_TIMEOUT_MS = 3000

// module-level singleton: only one delete button can be in pending state at a time app-wide

// int for user id, str for cat or subcat id like 'cat-3' or 'sub-3'
const pendingId = ref(null)
let timer = null

export function useConfirm() {
    function confirm(id) {
        if (pendingId.value === id) {
            clearTimeout(timer)
            pendingId.value = null
            return true  // second click, confirmed
        }
        clearTimeout(timer)
        pendingId.value = id
        timer = setTimeout(() => {
            pendingId.value = null
        }, CONFIRM_TIMEOUT_MS)
        return false  // first click, pending
    }

    return {pendingId, confirm}
}
