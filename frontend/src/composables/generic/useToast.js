import {ref} from 'vue'
import {store} from '../../store.js'

const TOAST_DURATION_MS = 4000

const message = ref(null)
const type = ref('success')
let timer = null

export function useToast() {
    function toast(msg, newType = 'success') {
        // logged out: the login page has no AppToast, the message would pop up after the next login
        if (!store.user) return
        clearTimeout(timer)

        message.value = msg
        type.value = newType

        timer = setTimeout(() => {
            message.value = null
        }, TOAST_DURATION_MS)
    }

    // single message and type for the whole app, rendered by AppToast.vue
    // toast(msg, newType) shows msg as 'success' or 'error' for 4s, a new call replaces the current one
    // read `message` and `type`, write via `toast()`
    return {
        message,
        type,
        toast,
    }
}
