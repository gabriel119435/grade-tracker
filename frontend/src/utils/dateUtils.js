// picks the century that puts the 2-digit year closest to the current year
function inferFullYear(twoDigitYear) {
    const currentYear = new Date().getFullYear()
    const century = Math.floor(currentYear / 100)
    const candidates = [
        // example: current year is 2100, input is 99:
        // 1999, 2099 and 2199, closest to 2100 is 2099

        // example: current year is 2026, input is 99:
        // 1999, 2099 and 2199, closest is 1999
        (century - 1) * 100 + twoDigitYear,
        century * 100 + twoDigitYear,
        (century + 1) * 100 + twoDigitYear
    ]
    return String(candidates.reduce((a, b) => Math.abs(a - currentYear) <= Math.abs(b - currentYear) ? a : b))
}

// converts ISO (YYYY-MM-DD) to locale display format, for display
export function localizeDate(normalizedDate, localDateFormat) {
    const [year, month, day] = normalizedDate.split('-')
    return localDateFormat
        .replace('YYYY', year)
        .replace('YY', year.slice(-2))
        .replace('MM', month)
        .replace('DD', day)
}

// converts a complete locale display date to ISO (YYYY-MM-DD), caller must pass a complete string
function normalizeDate(displayDate, localDateFormat) {
    const yearLength = localDateFormat.includes('YYYY') ? 4 : 2
    const yearPosition = localDateFormat.indexOf(yearLength === 4 ? 'YYYY' : 'YY')
    const year = displayDate.slice(yearPosition, yearPosition + yearLength)
    const fullYear = yearLength === 2 ? inferFullYear(parseInt(year)) : year
    const monthPosition = localDateFormat.indexOf('MM')
    const month = displayDate.slice(monthPosition, monthPosition + 2)
    const dayPosition = localDateFormat.indexOf('DD')
    const day = displayDate.slice(dayPosition, dayPosition + 2)
    return `${fullYear}-${month}-${day}`
}

function validateNormalizedDate(normalizedDate) {
    const year = parseInt(normalizedDate.slice(0, 4))
    const month = parseInt(normalizedDate.slice(5, 7))
    const day = parseInt(normalizedDate.slice(8, 10))
    if (isNaN(year) || isNaN(month) || isNaN(day)) return false
    if (month < 1 || month > 12) return false
    const daysInMonth = new Date(year, month, 0).getDate()
    return !(day < 1 || day > daysInMonth);

}

// validates user input against the locale format, returns normalized date string if valid or null if invalid
export function validateLocalizedDate(localizedDate, localDateFormat) {
    if (localizedDate.length !== localDateFormat.length) return null
    for (let i = 0; i < localDateFormat.length; i++) {
        const isFormatLetter = /[A-Z]/.test(localDateFormat[i])
        if (!isFormatLetter && localizedDate[i] !== localDateFormat[i]) return null
    }
    const normalizedDate = normalizeDate(localizedDate, localDateFormat)
    return validateNormalizedDate(normalizedDate) ? normalizedDate : null
}