import {ref} from 'vue'

const TOAST_DURATION_MS = 4000

const message = ref(null)
const type = ref('success')
let timer = null

export function useToast() {
    function toast(msg, newType = 'success') {
        clearTimeout(timer)

        message.value = msg
        type.value = newType

        timer = setTimeout(
            () => {
                message.value = null
            },
            TOAST_DURATION_MS
        )
    }

    // single message and type for the whole app, rendered by AppToast.vue
    // toast(msg, newType) shows msg as 'success' or 'error' for 4s, a new call replaces the current one
    // read `message` and `type`, write via `toast()`
    return {
        message,
        type,
        toast
    }
}
