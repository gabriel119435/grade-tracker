import {ref} from 'vue'

// all values must be > 1; i18n uses plural-only words
export const LIMITS = [5, 10, 30]

export function useLimit(onChange) {
    const limit = ref(LIMITS[0]) // default value

    async function setLimit(value) {
        limit.value = value
        // js does not enforce function signatures: onChange(value) always passes the new integer,
        // but the callback can declare zero parameters and silently ignore it (student view: load())
        // or declare a parameter and use it (teacher view: (newLimit) => loadStudentGrades(..., newLimit))
        await onChange(value)
    }

    return {limit, setLimit}
}
