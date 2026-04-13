import {ref} from 'vue'

// all values must be > 1; i18n uses plural-only words
export const LIMITS = [5, 10, 30]

export function useLimit() {
    const limit = ref(LIMITS[0]) // default value

    function setLimit(value) {
        limit.value = value
    }

    return {limit, setLimit}
}
