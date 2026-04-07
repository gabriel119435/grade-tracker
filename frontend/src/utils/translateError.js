import {i18n} from '../i18n.js'

// translates a backend error code to the current locale string.
// falls back to "{code} not found" via the global missing handler in i18n.js.
export function translateError(code) {
    return i18n.global.t(`backend_errors.${code}`)
}
