import {describe, expect, it} from 'vitest'
import {localizeGrade, normalizeGrade, trunc1dp, validateNormalizedGrade, buildGradesIndex, classifyGradeEdits} from './gradeUtils.js'

describe('buildGradesIndex', () => {
    it('returns empty index for empty input', () => {
        expect(buildGradesIndex([])).toEqual({})
    })
    it('indexes a single grade by date and subcategoryId', () => {
        const data = [{name: 'serve', subcategories: [{id: 3, name: 'slice', grades: [{id: 10, date: '2024-01-31', value: 7.5}]}]}]
        expect(buildGradesIndex(data)).toEqual({'2024-01-31': {3: {id: 10, value: 7.5}}})
    })
    it('groups multiple subcategories under the same date', () => {
        const data = [{name: 'serve', subcategories: [
            {id: 3, name: 'slice', grades: [{id: 10, date: '2024-01-31', value: 7.5}]},
            {id: 4, name: 'spin',  grades: [{id: 11, date: '2024-01-31', value: 8.0}]},
        ]}]
        expect(buildGradesIndex(data)).toEqual({'2024-01-31': {3: {id: 10, value: 7.5}, 4: {id: 11, value: 8.0}}})
    })
    it('groups grades across multiple dates', () => {
        const data = [{name: 'serve', subcategories: [{id: 3, name: 'slice', grades: [
            {id: 10, date: '2024-01-31', value: 7.5},
            {id: 11, date: '2024-02-01', value: 8.0},
        ]}]}]
        expect(buildGradesIndex(data)).toEqual({
            '2024-01-31': {3: {id: 10, value: 7.5}},
            '2024-02-01': {3: {id: 11, value: 8.0}},
        })
    })
})

describe('classifyGradeEdits', () => {
    it('classifies a filled input with no saved grade as new', () => {
        const [result] = classifyGradeEdits({}, {'3': '7.5'}, '.')
        expect(result.state).toBe('new')
    })
    it('classifies an empty input with a saved grade as deleting', () => {
        const [result] = classifyGradeEdits({'3': {id: 10, value: 7.5}}, {'3': ''}, '.')
        expect(result.state).toBe('deleting')
    })
    it('classifies a changed input as updating', () => {
        const [result] = classifyGradeEdits({'3': {id: 10, value: 7.5}}, {'3': '8.0'}, '.')
        expect(result.state).toBe('updating')
    })
    it('classifies an unchanged input as unchanged', () => {
        const [result] = classifyGradeEdits({'3': {id: 10, value: 7.5}}, {'3': '7.5'}, '.')
        expect(result.state).toBe('unchanged')
    })
    it('classifies an empty input with no saved grade as unchanged', () => {
        const [result] = classifyGradeEdits({}, {'3': ''}, '.')
        expect(result.state).toBe('unchanged')
    })
    it('normalizes locale separator before comparing', () => {
        const [result] = classifyGradeEdits({'3': {id: 10, value: 7.5}}, {'3': '7,5'}, ',')
        expect(result.state).toBe('unchanged')
    })
    it('returns normalized value in result', () => {
        const [result] = classifyGradeEdits({}, {'3': '8,0'}, ',')
        expect(result.normalized).toBe('8.0')
    })
})

describe('normalizeGrade', () => {
    it('replaces comma separator with dot', () => {
        expect(normalizeGrade('7,5', ',')).toBe('7.5')
    })
    it('leaves dot separator unchanged', () => {
        expect(normalizeGrade('7.5', '.')).toBe('7.5')
    })
})

describe('localizeGrade', () => {
    it('replaces dot with comma separator', () => {
        expect(localizeGrade(7.5, ',')).toBe('7,5')
    })
    it('leaves dot separator unchanged', () => {
        expect(localizeGrade(7.5, '.')).toBe('7.5')
    })
    it('converts number to string', () => {
        expect(localizeGrade(8, '.')).toBe('8')
    })
})

describe('trunc1dp', () => {
    it('truncates extra decimals without rounding', () => {
        expect(trunc1dp(7.99)).toBe(7.9)
    })
    it('leaves exact 1dp unchanged', () => {
        expect(trunc1dp(8.5)).toBe(8.5)
    })
})

describe('validateNormalizedGrade', () => {
    it('accepts empty string', () => {
        expect(validateNormalizedGrade('')).toBe(true)
    })
    it('accepts integer value', () => {
        expect(validateNormalizedGrade('8')).toBe(true)
    })
    it('accepts value with one decimal', () => {
        expect(validateNormalizedGrade('8.5')).toBe(true)
    })
    it('accepts boundary 0', () => {
        expect(validateNormalizedGrade('0')).toBe(true)
    })
    it('accepts boundary 10', () => {
        expect(validateNormalizedGrade('10')).toBe(true)
    })
    it('rejects value above 10', () => {
        expect(validateNormalizedGrade('10.1')).toBe(false)
    })
    it('rejects negative value', () => {
        expect(validateNormalizedGrade('-1')).toBe(false)
    })
    it('rejects more than one decimal', () => {
        expect(validateNormalizedGrade('8.55')).toBe(false)
    })
    it('rejects non-numeric string', () => {
        expect(validateNormalizedGrade('abc')).toBe(false)
    })
})
