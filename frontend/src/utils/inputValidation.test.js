import {describe, expect, it} from 'vitest'
import {NAME_WORD_MAX_LENGTH, PASSWORD_MIN_LENGTH} from '../constants.js'
import {hasLeadingOrTrailingSpaces, isNameWordTooLong, isPasswordTooShort} from './inputValidation.js'

// n letters, sized from the limits in constants.js
const chars = (n) => 'a'.repeat(n)

describe('hasLeadingOrTrailingSpaces', () => {
    it.each([
        [' teacher1', true],
        ['teacher1 ', true],
        ['teacher1', false],
        // inner spaces are allowed
        ['ana souza', false],
        ['', false],
    ])('%j returns %j', (value, expected) => {
        expect(hasLeadingOrTrailingSpaces(value)).toBe(expected)
    })
})

describe('isPasswordTooShort', () => {
    it.each([
        ['', false],
        [chars(PASSWORD_MIN_LENGTH - 1), true],
        [chars(PASSWORD_MIN_LENGTH), false],
    ])('%j returns %j', (value, expected) => {
        expect(isPasswordTooShort(value)).toBe(expected)
    })
})

describe('isNameWordTooLong', () => {
    it.each([
        ['', false],
        [chars(NAME_WORD_MAX_LENGTH), false],
        [chars(NAME_WORD_MAX_LENGTH + 1), true],
        [`ana ${chars(NAME_WORD_MAX_LENGTH)}`, false],
        [`ana ${chars(NAME_WORD_MAX_LENGTH + 1)}`, true],
    ])('%j returns %j', (value, expected) => {
        expect(isNameWordTooLong(value)).toBe(expected)
    })
})
