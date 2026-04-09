import {ref} from 'vue'

// all values must be > 1; i18n uses plural-only words
export const LIMITS = [5, 10, 30]

export function useLimit(onChange) {
    const limit = ref(LIMITS[0]) // default value

    async function setLimit(value) {
        limit.value = value
        await onChange(value)
    }

    return {limit, setLimit}
}
