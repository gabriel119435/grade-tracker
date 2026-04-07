import {reactive} from 'vue'

// plain reactive() instead of pinia; just 3 fields mutated in ~4 places
// pinia would add devtools visibility and $reset() but nothing else
export const store = reactive({
    user: null,           // {id: 1, username: 'admin', role: 'admin', locale: 'en'} or null if logged out
    sessionLoaded: false, // true once getMe() has resolved, regardless of whether a user was found
    locales: [],          // ['en', 'pt-br']
})