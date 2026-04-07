// replaces locale separator with '.'; for internal/backend use
// input is always a single user-typed value, so at most one separator is present
export function normalizeGrade(localeValue, separator) {
    return localeValue.replace(separator, '.')
}

// replaces '.' with locale separator; for display
export function localizeGrade(normalizedValue, separator) {
    return String(normalizedValue).replace('.', separator)
}

export function trunc1dp(x) {
    return Math.trunc(x * 10) / 10
}

// receives api response array, returns grades keyed by date then subcategoryId for O(1) lookup
// input:  [{name: 'serve', subcategories: [{id: 3, name: 'slice', grades: [{id: 10, date: '2024-01-31', value: 7.5}]}]}]
// output: {'2024-01-31': {3: {id: 10, value: 7.5}}}
export function buildGradesIndex(data) {
    const index = {}
    for (const cat of data) {
        for (const sub of cat.subcategories) {
            for (const g of sub.grades) {
                if (!index[g.date]) index[g.date] = {}
                index[g.date][sub.id] = {id: g.id, value: g.value}
            }
        }
    }
    return index
}

// classifies each grade edit as 'new' | 'updating' | 'deleting' | 'unchanged'
// oldGrades: {3: {id: 10, value: 7.5}} -- saved grades for the selected date, keyed by subcategoryId
// newGrades: {3: '7.5', 4: ''} -- what the user typed, keyed by subcategoryId
// returns: [{subcategoryId: '3', original: {id: 10, value: 7.5}, normalized: '8.0', state: 'updating'}, ...]
export function classifyGradeEdits(oldGrades, newGrades, separator) {
    return Object.entries(newGrades).map(([subcategoryId, input]) => {
        const original = oldGrades[subcategoryId]
        const normalized = normalizeGrade(input, separator)
        let state
        if (!original && input !== '') state = 'new'
        else if (original && input === '') state = 'deleting'
        else if (original && input !== '' && Number(normalized) !== original.value) state = 'updating'
        else state = 'unchanged'
        return {subcategoryId, original, normalized, state}
    })
}

// validates an already-normalized grade string (decimal separator is always '.')
// returns true if valid, false if invalid
export function validateNormalizedGrade(normalizedValue) {
    if (normalizedValue === '') return true
    const n = Number(normalizedValue)
    if (isNaN(n)) return false
    if (n < 0 || n > 10) return false
    return trunc1dp(n) === n
}
