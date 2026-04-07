import {ref} from 'vue'

export function useLoading() {
    // ref wraps the value in .value so vue can track changes to a primitive
    // declared inside the function so each useLoading() call gets its own independent loading state
    const loading = ref(false)

    async function withLoading(fn) {
        // if called while another function is running, simply does not call fn
        if (loading.value) return
        loading.value = true
        try {
            await fn()
        } finally {
            loading.value = false
        }
    }

    return {loading, withLoading}
}