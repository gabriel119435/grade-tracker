// shared constants

// block below mirrors backend/app/constants.py, change both together
export const PASSWORD_MIN_LENGTH = 8
export const PASSWORD_MAX_LENGTH = 25
export const USERNAME_MAX_LENGTH = 25
export const NAME_MAX_LENGTH = 25
export const NAME_WORD_MAX_LENGTH = 15
// every ui language, one translation file per entry in src/locales
export const LOCALES = ['en', 'pt-br']
export const DEFAULT_LOCALE = 'pt-br'

// values for locale slots like {password_min}
export const LIMIT_PARAMS = {
    password_min: PASSWORD_MIN_LENGTH,
    password_max: PASSWORD_MAX_LENGTH,
    username_max: USERNAME_MAX_LENGTH,
    name_max: NAME_MAX_LENGTH,
    word_max: NAME_WORD_MAX_LENGTH,
}

// grade history sizes offered by the limit buttons, default first
// all values must be > 1, i18n uses plural-only words
export const GRADE_HISTORY_LIMITS = [5, 10, 30]
