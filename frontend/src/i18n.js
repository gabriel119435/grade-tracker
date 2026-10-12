import {createI18n} from 'vue-i18n'
import en from './locales/en.js'
import ptBr from './locales/pt-br.js'
import {DEFAULT_LOCALE} from './constants.js'

export const i18n = createI18n(
    {
        legacy: false,
        locale: DEFAULT_LOCALE,
        messages: {en, 'pt-br': ptBr},
        // missing key: 'backend_errors.foo_bar' -> 'foo_bar not found'
        missing: (locale, key) => `${key.split('.').at(-1)} not found`,
    }
)
