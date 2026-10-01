import {PASSWORD_MIN_LENGTH} from './limits.js'

export function hasLeadingOrTrailingSpaces(value) { return value.length > 0 && value !== value.trim() }
export function isTooShort(value) { return value.length > 0 && value.length < PASSWORD_MIN_LENGTH }
