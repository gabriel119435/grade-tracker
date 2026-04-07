import {createI18n} from 'vue-i18n'
import en from './locales/en.js'
import ptBr from './locales/pt-br.js'

export const i18n = createI18n(
    {
        legacy: false,
        locale: 'pt-br',
        messages: {en, 'pt-br': ptBr},
        // 'backend_errors.not_found' into 'not_found'
        missing: (locale, key) => `${key.split('.').at(-1)} not found`,
    }
)
