import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import router from './router/index.js'
import {i18n} from './i18n.js'
import {clickOutside} from './directives/clickOutside.js'
import {setSessionLostHandler} from './api/request.js'
import {clearSession} from './store.js'

// session gone or replaced: reset it, the guard's getMe on /login decides where this tab lands
// 401: no session, stays on /login; 403: another user's cookie, goes to that user's home
setSessionLostHandler(async () => {
    clearSession()
    await router.push('/login')
})

createApp(App)
    .use(router)
    .use(i18n)
    // registered as v-click-outside in templates, automatically added by vue
    .directive('click-outside', clickOutside)
    .mount('#app')
