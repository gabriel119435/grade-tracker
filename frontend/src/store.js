import {reactive} from 'vue'
import {i18n} from './i18n.js'
import {DEFAULT_LOCALE} from './constants.js'

export const store = reactive({
    // {id: 1, username: 'admin', role: 'admin', locale: 'en', arena_name: 'arena'} or null if logged out
    user: null,
    // true once getMe() answered, false again after clearSession()
    sessionLoaded: false,
    // true when getMe() fails
    sessionCheckFailed: false,
})

// logged-out state: user, session check and locale back to defaults, used by logout and by any 401
export function clearSession() {
    store.user = null
    store.sessionLoaded = false
    i18n.global.locale.value = DEFAULT_LOCALE
}
