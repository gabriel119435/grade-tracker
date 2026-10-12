// converts ISO (YYYY-MM-DD) to locale display format, for display
export function localizeDate(normalizedDate, localDateFormat) {
    const [year, month, day] = normalizedDate.split('-')
    return localDateFormat
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
}

// converts a complete locale display date to ISO (YYYY-MM-DD), caller must pass a complete string
function normalizeDate(displayDate, localDateFormat) {
    const yearPosition = localDateFormat.indexOf('YYYY')
    const year = displayDate.slice(yearPosition, yearPosition + 4)
    const monthPosition = localDateFormat.indexOf('MM')
    const month = displayDate.slice(monthPosition, monthPosition + 2)
    const dayPosition = localDateFormat.indexOf('DD')
    const day = displayDate.slice(dayPosition, dayPosition + 2)
    return `${year}-${month}-${day}`
}

function validateNormalizedDate(normalizedDate) {
    const year = parseInt(normalizedDate.slice(0, 4))
    const month = parseInt(normalizedDate.slice(5, 7))
    const day = parseInt(normalizedDate.slice(8, 10))
    // 4 digits already cap it at 9999 max. python's date starts at year 1
    if (year < 1) return false
    if (month < 1 || month > 12) return false
    // js months count from 0, so 1-based `month` here means the next month
    // day 0 of the next month is the last day of this month: its date is this month's length
    const daysInMonth = new Date(year, month, 0).getDate()
    return day >= 1 && day <= daysInMonth
}

// today's date on the user's own calendar, as 'YYYY-MM-DD'
// getFullYear, getMonth and getDate read the local timezone, not utc (toISOString would give the utc day)
export function localToday() {
    const now = new Date()
    const year = now.getFullYear()
    // getMonth counts from 0: january is 0
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
}

// validates user input against the locale format, returns normalized date string if valid or null if invalid
export function validateLocalizedDate(localizedDate, localDateFormat) {
    if (localizedDate.length !== localDateFormat.length) return null
    for (let i = 0; i < localDateFormat.length; i++) {
        const isFormatLetter = /[YMD]/.test(localDateFormat[i])
        // format letters (YMD) must be digits, anything else must match the format exactly: '-' or '/'
        const matches = isFormatLetter ? /\d/.test(localizedDate[i]) : localizedDate[i] === localDateFormat[i]
        if (!matches) return null
    }
    const normalizedDate = normalizeDate(localizedDate, localDateFormat)
    return validateNormalizedDate(normalizedDate) ? normalizedDate : null
}
