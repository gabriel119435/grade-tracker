// replaces '.' with locale separator; for display
export function localizeGrade(value, separator) {
    return String(value).replace('.', separator)
}

// the only place that turns cell text into a grade: 0 to 10, at most one decimal, locale separator only
// '' with any separator -> {valid:true, value:null}
// '7,5' with ',' -> {valid:true, value:7.5}
// '7.5', ' 7', '+5', '-0', '05', '1e1', '0x5', '7,', '10,5' with ',' -> {valid:false, value:null}
export function parseGrade(text, separator) {
    // empty cell: no grade, not an error
    if (text === '') return {valid: true, value: null}
    // '7,5' -> ['7', '5']; '7' -> ['7']; '7,5,3' -> ['7', '5', '3']
    const parts = text.split(separator)
    // more than one separator: '7,5,3'
    if (parts.length > 2) return {valid: false, value: null}
    const [whole, decimal] = parts
    // whole part must be exactly 0 to 9 or 10
    if (!/^(10|\d)$/.test(whole)) return {valid: false, value: null}
    // decimal part, if a separator was typed, must be exactly one digit: rejects '7,', '7,55', '7,a'
    if (decimal !== undefined && !/^\d$/.test(decimal)) return {valid: false, value: null}
    const value = Number(decimal === undefined ? whole : `${whole}.${decimal}`)
    // '10,5' passes both checks above but is above the max grade
    if (value > 10) return {valid: false, value: null}
    return {valid: true, value}
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

// classifies each cell as 'error' | 'new' | 'updating' | 'deleting' | 'unchanged'
// oldGrades: {3: {id: 10, value: 7.5}} -- saved grades for the selected date, keyed by subcategoryId
// newGrades: {3: '8,0', 4: ''} -- cell texts, keyed by subcategoryId
// returns: [{subcategoryId: '3', original: {id: 10, value: 7.5}, value: 8, state: 'updating'}, ...]
export function classifyGradeEdits(oldGrades, newGrades, separator) {
    return Object.entries(newGrades).map(([subcategoryId, text]) => {
        const original = oldGrades[subcategoryId]
        const {valid, value} = parseGrade(text, separator)
        let state
        if (!valid) state = 'error'
        else if (!original && value !== null) state = 'new'
        else if (original && value === null) state = 'deleting'
        else if (original && value !== original.value) state = 'updating'
        else state = 'unchanged'
        return {subcategoryId, original, value, state}
    })
}
