import {createRouter, createWebHistory} from 'vue-router'
import {getLocales, getMe} from '../api/routes/auth.js'
import {store} from '../store.js'
import {i18n} from '../i18n.js'
import LoginView from '../views/LoginView.vue'
import BaseLayout from '../views/BaseLayout.vue'
import TeachersView from '../views/admin/TeachersView.vue'
import TabLayout from '../views/TabLayout.vue'
import CategoriesView from '../views/teacher/CategoriesView.vue'
import StudentsView from '../views/teacher/StudentsView.vue'
import TeacherGradesView from '../views/teacher/GradesView.vue'
import StudentGradesView from '../views/student/GradesView.vue'

const HOME_URL = {admin: '/admin', teacher: '/teacher', student: '/student'}

const routes = [
    {path: '/login', component: LoginView},
    {
        path: '/admin',
        component: BaseLayout,
        meta: {allowed_role: 'admin'},
        children: [
            {path: '', redirect: '/admin/teachers'},
            {path: 'teachers', component: TeachersView}
        ]
    },
    {
        path: '/teacher',
        component: TabLayout,
        meta: {allowed_role: 'teacher'},
        children: [
            {path: '', redirect: '/teacher/categories'},
            {path: 'categories', component: CategoriesView},
            {path: 'students', component: StudentsView},
            {path: 'grades', component: TeacherGradesView}
        ]
    },
    {
        path: '/student',
        component: BaseLayout,
        meta: {allowed_role: 'student'},
        children: [
            {path: '', component: StudentGradesView}
        ]
    },
    {path: '/', redirect: '/login'}
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// runs before every routing, returns true if allowed, string url if redirected; exported for testing
// named following vue router convention, not standard verb-first method naming
export async function navigationGuard(to) {
    if (!store.sessionLoaded) {
        try {
            const [userResponse, locales] = await Promise.all([getMe(), getLocales()])
            store.user = userResponse.user
            store.locales = locales
            if (userResponse.user?.locale) i18n.global.locale.value = userResponse.user.locale
        } catch (err) {
            console.error('auth error:', err)
            // network failure, treat as logged out
        }
        store.sessionLoaded = true
    }

    // send not logged-in user to login page
    if (!store.user) return to.path === '/login' ? true : '/login'
    else {
        // if logged-in user tries /login or unmatched url, send him home
        if (to.path === '/login' || !to.matched.length) return HOME_URL[store.user.role]
        // if user is trying to access a not allowed page, send him home
        if (to.meta.allowed_role && store.user.role !== to.meta.allowed_role) return HOME_URL[store.user.role]

        return true
    }
}

router.beforeEach(navigationGuard)

export default router
