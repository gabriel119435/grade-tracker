import {nextTick, ref} from 'vue'

export function useLoading() {
    const loading = ref(false)

    async function withLoading(fn) {
        if (loading.value) return
        const focused = document.activeElement
        loading.value = true
        try {
            await fn()
        } finally {
            loading.value = false
            // a button disabled while focused drops focus to <body>
            // after vue re-enables it, focus goes back, unless the button is gone (deleted row, new page)
            await nextTick()
            if (document.activeElement === document.body && focused?.isConnected) focused.focus()
        }
    }

    // slow request plus repeated clicks can send the same action several times
    // withLoading(fn) runs fn with `loading` true, calls made meanwhile are ignored
    // read `loading` to disable buttons, write via `withLoading()`
    return {loading, withLoading}
}
