import {i18n} from '../i18n.js'
import {LIMIT_PARAMS} from '../constants.js'

// translates an error code (backend, nginx, request.js or a live input check mirroring a backend rule)
// to the current locale string
// messages without slots ignore LIMIT_PARAMS
// unknown codes fall back to the missing handler in i18n.js
export function translateError(code) {
    return i18n.global.t(`backend_errors.${code}`, LIMIT_PARAMS)
}
