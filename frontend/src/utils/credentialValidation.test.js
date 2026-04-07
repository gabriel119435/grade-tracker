import {describe, expect, it} from 'vitest'
import {hasLeadingOrTrailingSpaces, isTooShort} from './credentialValidation.js'

describe('hasLeadingOrTrailingSpaces', () => {
    it('returns true for leading space', () => {
        expect(hasLeadingOrTrailingSpaces(' teacher1')).toBe(true)
    })
    it('returns true for trailing space', () => {
        expect(hasLeadingOrTrailingSpaces('teacher1 ')).toBe(true)
    })
    it('returns false for clean value', () => {
        expect(hasLeadingOrTrailingSpaces('teacher1')).toBe(false)
    })
    it('returns false for empty string', () => {
        expect(hasLeadingOrTrailingSpaces('')).toBe(false)
    })
})

describe('isTooShort', () => {
    it('returns true for value shorter than 8 characters', () => {
        expect(isTooShort('abc')).toBe(true)
    })
    it('returns false for value with exactly 8 characters', () => {
        expect(isTooShort('abcdefgh')).toBe(false)
    })
    it('returns false for empty string', () => {
        expect(isTooShort('')).toBe(false)
    })
})
