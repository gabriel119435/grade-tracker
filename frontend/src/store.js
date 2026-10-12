import {reactive} from 'vue'

export const store = reactive({
    user: null,                // {id: 1, username: 'admin', role: 'admin', locale: 'en'} or null if logged out
    sessionLoaded: false,      // true once getMe() answered, false again after logout
    sessionCheckFailed: false, // true when getMe() fails
})