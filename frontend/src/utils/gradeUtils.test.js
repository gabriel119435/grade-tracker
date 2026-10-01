import {describe, expect, it} from 'vitest'
import {localizeGrade, parseGrade, buildGradesIndex, classifyGradeEdits} from './gradeUtils.js'

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
    it('returns parsed value in result', () => {
        const [result] = classifyGradeEdits({}, {'3': '8,5'}, ',')
        expect(result.value).toBe(8.5)
    })
    it('classifies invalid text as error', () => {
        const [result] = classifyGradeEdits({'3': {id: 10, value: 7.5}}, {'3': '7,5'}, '.')
        expect(result.state).toBe('error')
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

describe('parseGrade', () => {
    it('accepts empty string as no grade', () => {
        expect(parseGrade('', ',')).toEqual({valid: true, value: null})
    })
    it('accepts integer value', () => {
        expect(parseGrade('8', ',')).toEqual({valid: true, value: 8})
    })
    it('accepts value with one decimal and locale separator', () => {
        expect(parseGrade('8,5', ',')).toEqual({valid: true, value: 8.5})
        expect(parseGrade('8.5', '.')).toEqual({valid: true, value: 8.5})
    })
    it('accepts boundaries 0 and 10', () => {
        expect(parseGrade('0', ',')).toEqual({valid: true, value: 0})
        expect(parseGrade('10', ',')).toEqual({valid: true, value: 10})
    })
    it.each(['10,1', '11', '-1', '-0', '8,55', 'abc', ' ', ' 7 ', '+5', '05', '1e1', '0x5', '7,', ',5', '7,5,3', '8.5'])(
        'rejects %j with comma separator', (text) => {
            expect(parseGrade(text, ',')).toEqual({valid: false, value: null})
        })
})
