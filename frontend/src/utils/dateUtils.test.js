import {describe, expect, it} from 'vitest'
import {localizeDate, validateLocalizedDate} from './dateUtils.js'

describe('localizeDate', () => {
    it('formats iso date to DD/MM/YYYY', () => {
        expect(localizeDate('2024-01-15', 'DD/MM/YYYY')).toBe('15/01/2024')
    })
    it('formats iso date to MM/DD/YYYY', () => {
        expect(localizeDate('2024-01-15', 'MM/DD/YYYY')).toBe('01/15/2024')
    })
    it('formats iso date to YYYY-MM-DD', () => {
        expect(localizeDate('2024-01-15', 'YYYY-MM-DD')).toBe('2024-01-15')
    })
    it('formats iso date to DD/MM/YY', () => {
        expect(localizeDate('2024-01-15', 'DD/MM/YY')).toBe('15/01/24')
    })
})

describe('validateLocalizedDate', () => {
    it('returns normalized iso date for valid DD/MM/YYYY input', () => {
        expect(validateLocalizedDate('15/01/2024', 'DD/MM/YYYY')).toBe('2024-01-15')
    })
    it('returns normalized iso date for valid MM/DD/YYYY input', () => {
        expect(validateLocalizedDate('01/15/2024', 'MM/DD/YYYY')).toBe('2024-01-15')
    })
    it('returns null for wrong length', () => {
        expect(validateLocalizedDate('15/1/2024', 'DD/MM/YYYY')).toBeNull()
    })
    it('returns null for wrong separator', () => {
        expect(validateLocalizedDate('15-01-2024', 'DD/MM/YYYY')).toBeNull()
    })
    it('returns null for invalid day 0', () => {
        expect(validateLocalizedDate('00/01/2024', 'DD/MM/YYYY')).toBeNull()
    })
    it('returns null for invalid month 13', () => {
        expect(validateLocalizedDate('01/13/2024', 'DD/MM/YYYY')).toBeNull()
    })
    it('returns null for day exceeding month length', () => {
        expect(validateLocalizedDate('30/02/2024', 'DD/MM/YYYY')).toBeNull()
    })
    it('accepts last day of month', () => {
        expect(validateLocalizedDate('29/02/2024', 'DD/MM/YYYY')).toBe('2024-02-29')
    })
    it('returns null for 2-digit year input with 4-digit format', () => {
        expect(validateLocalizedDate('15/01/24', 'DD/MM/YYYY')).toBeNull()
    })
})
