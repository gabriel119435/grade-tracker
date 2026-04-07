import {createApp} from 'vue'
import './style.css'
import App from './App.vue'
import router from './router/index.js'
import {i18n} from './i18n.js'
import {clickOutside} from './directives/clickOutside.js'

createApp(App)
    .use(router)
    .use(i18n)
    // registered as v-click-outside in templates, automatically added by vue
    .directive('click-outside', clickOutside)
    .mount('#app')