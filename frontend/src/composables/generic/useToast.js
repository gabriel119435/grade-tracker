import {ref} from 'vue'

const TOAST_DURATION_MS = 4000

// module-level singleton: any component calling toast() updates the same refs
const message = ref(null)
const type = ref('success')
let timer = null

export function useToast() {
    function toast(msg, kind = 'success') {
        clearTimeout(timer)
        message.value = msg
        type.value = kind
        // setTimeout will return a numeric id for a scheduled event from browser
        timer = setTimeout(() => {
            message.value = null
        }, TOAST_DURATION_MS)
    }

    return {
        message,
        type,
        toast
    }
}
