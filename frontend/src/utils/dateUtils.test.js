import {afterEach, describe, expect, it, vi} from 'vitest'
import {localizeDate, localToday, validateLocalizedDate} from './dateUtils.js'

describe('localizeDate', () => {
    it.each([
        ['DD/MM/YYYY', '15/01/2024'],
        ['MM/DD/YYYY', '01/15/2024'],
        ['YYYY-MM-DD', '2024-01-15'],
    ])('formats 2024-01-15 with %s as %j', (format, expected) => {
        expect(localizeDate('2024-01-15', format)).toBe(expected)
    })
})

describe('localToday', () => {
    afterEach(() => vi.useRealTimers())

    // new Date(year, monthIndex, ...) builds a local time on this machine's clock
    it.each([
        ['the local day late in the evening, not the utc one', new Date(2026, 8, 30, 23, 30), '2026-09-30'],
        ['a single-digit month and day with a leading zero', new Date(2026, 0, 5, 12, 0), '2026-01-05'],
    ])('returns %s', (_, now, expected) => {
        vi.useFakeTimers()
        vi.setSystemTime(now)
        expect(localToday()).toBe(expected)
    })
})

describe('validateLocalizedDate', () => {
    it.each([
        ['15/01/2024', 'DD/MM/YYYY', '2024-01-15'],
        ['01/15/2024', 'MM/DD/YYYY', '2024-01-15'],
        ['2024-01-15', 'YYYY-MM-DD', '2024-01-15'],
        // last day of february in a leap year
        ['29/02/2024', 'DD/MM/YYYY', '2024-02-29'],
    ])('accepts %j with %s as %j', (text, format, expected) => {
        expect(validateLocalizedDate(text, format)).toBe(expected)
    })

    // inputs grouped by reason, prettier would put each on its own line
    // prettier-ignore
    const invalidDates = [
        // wrong length
        '15/1/2024', '15/01/24',
        // wrong separator
        '15-01-2024',
        // letter in a digit position
        '15/01/2a24',
        // year 0, python's date starts at year 1
        '01/01/0000',
        // month out of range
        '15/00/2024', '15/13/2024',
        // day out of range
        '00/01/2024', '30/02/2024',
        // february 29 outside a leap year
        '29/02/2023',
    ]

    it.each(invalidDates)('rejects %j with DD/MM/YYYY', (text) => {
        expect(validateLocalizedDate(text, 'DD/MM/YYYY')).toBeNull()
    })
})
