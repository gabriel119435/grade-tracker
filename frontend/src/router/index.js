import {createRouter, createWebHistory} from 'vue-router'
import {getMe} from '../api/routes/auth.js'
import {store} from '../store.js'
import {i18n} from '../i18n.js'
import {HOME_URL} from '../constants.js'
import BaseLayout from '../layouts/BaseLayout.vue'
import TabLayout from '../layouts/TabLayout.vue'
import LoginView from '../views/LoginView.vue'
import AdminView from '../views/admin/AdminView.vue'
import CategoriesView from '../views/teacher/CategoriesView.vue'
import StudentsView from '../views/teacher/StudentsView.vue'
import TeacherGradesView from '../views/teacher/GradesView.vue'
import StudentGradesView from '../views/student/GradesView.vue'

const routes = [
    {
        path: '/admin',
        component: BaseLayout,
        // custom field read by navigationGuard: only this role may open the route and its children
        meta: {allowed_role: 'admin'},
        children: [{path: '', component: AdminView}],
    },
    {
        path: '/teacher',
        component: TabLayout,
        meta: {allowed_role: 'teacher'},
        children: [
            {path: '', redirect: '/teacher/categories'},
            {path: 'categories', component: CategoriesView},
            {path: 'students', component: StudentsView},
            {path: 'grades', component: TeacherGradesView},
        ],
    },
    {
        path: '/student',
        component: BaseLayout,
        meta: {allowed_role: 'student'},
        children: [{path: '', component: StudentGradesView}],
    },
    {
        path: '/',
        redirect: '/login',
    },
    {
        path: '/login',
        component: LoginView,
    },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// runs before every routing, returns true if allowed, string url if redirected. exported for testing
// name following vue router convention
export async function navigationGuard(to) {
    if (!store.sessionLoaded) {
        const userResponse = await getMe()
        // failed session check: treated as logged out, the login page shows why
        store.user = userResponse.error ? null : userResponse.user
        store.sessionCheckFailed = Boolean(userResponse.error)
        if (store.user?.locale) i18n.global.locale.value = store.user.locale
        store.sessionLoaded = true
    }

    // send not logged-in user to login page
    if (!store.user) return to.path === '/login' ? true : '/login'

    // logged-in user on /login or an unmatched url goes to their home
    if (to.path === '/login' || !to.matched.length) return HOME_URL[store.user.role]
    // logged-in user on another role's page goes to their home
    if (to.meta.allowed_role && store.user.role !== to.meta.allowed_role) return HOME_URL[store.user.role]

    return true
}

router.beforeEach(navigationGuard)

export default router
