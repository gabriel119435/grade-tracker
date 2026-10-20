import {beforeEach, describe, expect, it, vi} from 'vitest'
import {getMe} from '../api/routes/auth.js'
import {DEFAULT_LOCALE} from '../constants.js'
import {i18n} from '../i18n.js'
import {store} from '../store.js'
import {navigationGuard} from './index.js'

// vi.mock('path', factory): every import of 'path', here and in index.js, gets the factory's return value
// vi.fn() is a no-op that records its calls, mockResolvedValue sets its answer per test
// vitest clears recorded calls before each test, clearMocks is on by default
vi.mock('../api/routes/auth.js', () => ({
    getMe: vi.fn(),
}))

// createRouter returns a fake router with a no-op beforeEach, so index.js can register the guard
// createWebHistory reads window.location, node has no window: the real module crashes on import
vi.mock('vue-router', () => ({
    createRouter: vi.fn(() => ({beforeEach: vi.fn()})),
    createWebHistory: vi.fn(),
}))

// stub vue components so the router module loads without a dom
vi.mock('../views/LoginView.vue', () => ({default: {}}))
vi.mock('../layouts/BaseLayout.vue', () => ({default: {}}))
vi.mock('../layouts/TabLayout.vue', () => ({default: {}}))
vi.mock('../views/admin/AdminView.vue', () => ({default: {}}))
vi.mock('../views/teacher/CategoriesView.vue', () => ({default: {}}))
vi.mock('../views/teacher/StudentsView.vue', () => ({default: {}}))
vi.mock('../views/teacher/GradesView.vue', () => ({default: {}}))
vi.mock('../views/student/GradesView.vue', () => ({default: {}}))

// minimal route object with the fields the guard reads, route(path) alone uses the defaults
function route(path, {matched = [{}], meta = {}} = {}) {
    return {path, matched, meta}
}

beforeEach(() => {
    store.user = null
    store.sessionCheckFailed = false
    i18n.global.locale.value = DEFAULT_LOCALE
    // skip getMe by default, session tests set false to run it
    store.sessionLoaded = true
})

describe('session loading', () => {
    beforeEach(() => {
        store.sessionLoaded = false
    })

    it('calls getMe once and marks the session loaded', async () => {
        getMe.mockResolvedValue({user: null})
        await navigationGuard(route('/login'))
        expect(getMe).toHaveBeenCalledOnce()
        expect(store.sessionLoaded).toBe(true)
    })
    it('stores the user and applies their locale', async () => {
        getMe.mockResolvedValue({user: {id: 1, role: 'teacher', locale: 'en'}})
        await navigationGuard(route('/teacher/categories', {meta: {allowed_role: 'teacher'}}))
        expect(store.user).toEqual({id: 1, role: 'teacher', locale: 'en'})
        expect(i18n.global.locale.value).toBe('en')
    })
    it('treats a failed check as logged out and flags it for the login page', async () => {
        getMe.mockResolvedValue({error: 'network_error'})
        expect(await navigationGuard(route('/teacher/categories'))).toBe('/login')
        expect(store.user).toBeNull()
        expect(store.sessionCheckFailed).toBe(true)
    })
    it('clears the failure flag on a later successful check', async () => {
        store.sessionCheckFailed = true
        getMe.mockResolvedValue({user: null})
        await navigationGuard(route('/login'))
        expect(store.sessionCheckFailed).toBe(false)
    })
    it('skips getMe when the session is already loaded', async () => {
        store.sessionLoaded = true
        await navigationGuard(route('/login'))
        expect(getMe).not.toHaveBeenCalled()
    })
})

describe('access', () => {
    it.each([
        // not logged in: only /login
        [null, '/login', {}, true],
        [null, '/teacher/categories', {}, '/login'],
        // logged in: /login and unmatched urls go home
        ['teacher', '/login', {}, '/teacher'],
        ['teacher', '/nonexistent', {matched: []}, '/teacher'],
        // own role allowed, another role's page goes home
        ['admin', '/admin', {meta: {allowed_role: 'admin'}}, true],
        ['admin', '/teacher/categories', {meta: {allowed_role: 'teacher'}}, '/admin'],
        ['teacher', '/teacher/categories', {meta: {allowed_role: 'teacher'}}, true],
        ['teacher', '/admin', {meta: {allowed_role: 'admin'}}, '/teacher'],
        ['student', '/student', {meta: {allowed_role: 'student'}}, true],
        ['student', '/teacher/grades', {meta: {allowed_role: 'teacher'}}, '/student'],
        // matched route with no role rule: open to any logged-in user
        ['student', '/other', {}, true],
    ])('role %j on %j %j returns %j', async (role, path, options, expected) => {
        store.user = role && {id: 1, role}
        expect(await navigationGuard(route(path, options))).toBe(expected)
    })
})
