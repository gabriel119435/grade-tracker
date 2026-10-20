import {describe, expect, it} from 'vitest'
import {classifyGradeEdits, localizeGrade, parseGrade} from './gradeUtils.js'

describe('localizeGrade', () => {
    it.each([
        [7.5, ',', '7,5'],
        [7.5, '.', '7.5'],
        [8, ',', '8'],
    ])('localizes %j with %j as %j', (value, separator, expected) => {
        expect(localizeGrade(value, separator)).toBe(expected)
    })
})

describe('parseGrade', () => {
    it.each([
        ['', ',', null],
        ['8', ',', 8],
        ['8,5', ',', 8.5],
        ['8.5', '.', 8.5],
        ['0', ',', 0],
        ['10', ',', 10],
        ['10,0', ',', 10],
    ])('accepts %j with %j as %j', (text, separator, value) => {
        expect(parseGrade(text, separator)).toEqual({valid: true, value})
    })

    // short inputs packed per line, prettier would put each on its own line
    // prettier-ignore
    const invalidTexts = [
        '10,1', '11', '-1', '-0', '8,55', '7,a', 'abc', ' ', ' 7 ',
        '+5', '05', '1e1', '0x5', '7,', ',5', '7,5,3', '8.5',
    ]

    it.each(invalidTexts)('rejects %j with comma separator', (text) => {
        expect(parseGrade(text, ',')).toEqual({valid: false, value: null})
    })
})

describe('classifyGradeEdits', () => {
    const saved = {3: {id: 10, value: 7.5}}

    it.each([
        ['new', {}, '7.5', '.'],
        ['deleting', saved, '', '.'],
        ['updating', saved, '8.0', '.'],
        ['unchanged', saved, '7.5', '.'],
        ['unchanged', {}, '', '.'],
        // locale separator normalized before comparing
        ['unchanged', saved, '7,5', ','],
        ['error', saved, '7,5', '.'],
    ])('classifies as %s: saved %j, cell %j, separator %j', (state, oldGrades, text, separator) => {
        const [result] = classifyGradeEdits(oldGrades, {3: text}, separator)
        expect(result.state).toBe(state)
    })
    it('returns one entry per cell with its id, saved grade and parsed value', () => {
        expect(classifyGradeEdits(saved, {3: '8,5', 4: ''}, ',')).toEqual([
            {subcategoryId: '3', original: {id: 10, value: 7.5}, value: 8.5, state: 'updating'},
            {subcategoryId: '4', original: undefined, value: null, state: 'unchanged'},
        ])
    })
})
