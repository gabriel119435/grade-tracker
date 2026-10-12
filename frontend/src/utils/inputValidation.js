import {NAME_WORD_MAX_LENGTH, PASSWORD_MIN_LENGTH} from '../constants.js'

// true when a non-empty value starts or ends with whitespace: ' ana', 'ana '
export function hasLeadingOrTrailingSpaces(value) {
    return value.length > 0 && value !== value.trim()
}

// true when a non-empty value is shorter than PASSWORD_MIN_LENGTH, empty is left to `required`
export function isPasswordTooShort(value) {
    return value.length > 0 && value.length < PASSWORD_MIN_LENGTH
}

// true when any space-separated word is longer than NAME_WORD_MAX_LENGTH
export function isNameWordTooLong(value) {
    return value.split(/\s+/).some(word => word.length > NAME_WORD_MAX_LENGTH)
}
