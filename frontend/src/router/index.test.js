import {beforeEach, describe, expect, it, vi} from 'vitest'
import {getLocales, getMe} from '../api/routes/auth.js'
import {store} from '../store.js'
import {navigationGuard} from './index.js'

// vi.mock('path', factory): whenever this test imports from 'path', vitest calls the factory once and uses its return value as the module
// vi.fn() produces a no-op that records calls. configure its return value per test with mockResolvedValue
// getMe and getLocales would make real http calls; replacing them with vi.fn() keeps tests isolated from the network
vi.mock('../api/routes/auth.js', () => ({
    getMe: vi.fn(),
    getLocales: vi.fn(),
}))

// window is a global object browsers inject into every js file, holding url, history, dom, fetch, etc; node has no browser so window doesn't exist
// createWebHistory reads window.location to initialize url tracking, crashing in node; mocking the module prevents that
// createRouter returns a fake router with a no-op beforeEach so index.js can call router.beforeEach(navigationGuard) without error
vi.mock('vue-router', () => ({
    // fake router instance with a no-op beforeEach
    createRouter: vi.fn(() => ({beforeEach: vi.fn()})),
    // just needs to not throw; returns undefined
    createWebHistory: vi.fn(),
}))

// stub vue components so the router module loads without a dom
vi.mock('../views/LoginView.vue', () => ({default: {}}))
vi.mock('../views/BaseLayout.vue', () => ({default: {}}))
vi.mock('../views/TabLayout.vue', () => ({default: {}}))
vi.mock('../views/admin/TeachersView.vue', () => ({default: {}}))
vi.mock('../views/teacher/CategoriesView.vue', () => ({default: {}}))
vi.mock('../views/teacher/StudentsView.vue', () => ({default: {}}))
vi.mock('../views/teacher/GradesView.vue', () => ({default: {}}))
vi.mock('../views/student/GradesView.vue', () => ({default: {}}))

// builds a minimal route object with the fields the guard reads
// = {} after the destructured second param means: if no second arg is passed, destructure {} instead of undefined (which would throw)
// matched = [{}] and meta = {} are the inner defaults used when those keys are absent from the second arg
function route(
    path,
    {
        matched = [{}],
        meta = {}
    } = {}
) {
    return {path, matched, meta}
}

beforeEach(() => {
    store.user = null
    // skip api calls by default; individual tests opt in by setting false
    store.sessionLoaded = true
    store.locales = []
    // resets call history on all vi.fn()s so one test's calls don't affect the next test's assertions
    vi.clearAllMocks()
})

describe('session loading', () => {
    it('calls getMe and getLocales on first navigation', async () => {
        store.sessionLoaded = false
        getMe.mockResolvedValue({user: null})
        getLocales.mockResolvedValue([])

        await navigationGuard(route('/login'))

        expect(getMe).toHaveBeenCalledOnce()
        expect(getLocales).toHaveBeenCalledOnce()
        expect(store.sessionLoaded).toBe(true)
    })

    it('sets store.user from getMe response', async () => {
        store.sessionLoaded = false
        getMe.mockResolvedValue({user: {id: 1, role: 'teacher', locale: 'en'}})
        getLocales.mockResolvedValue([])

        await navigationGuard(route('/teacher/categories', {meta: {allowed_role: 'teacher'}}))

        expect(store.user).toEqual({id: 1, role: 'teacher', locale: 'en'})
    })

    it('skips api calls when session is already loaded', async () => {
        store.sessionLoaded = true

        await navigationGuard(route('/login'))

        expect(getMe).not.toHaveBeenCalled()
    })
})

describe('not logged in', () => {
    it('allows /login', async () => {
        expect(await navigationGuard(route('/login'))).toBe(true)
    })

    it('redirects any other route to /login', async () => {
        expect(await navigationGuard(route('/teacher/categories'))).toBe('/login')
    })
})

describe('logged in as teacher', () => {
    beforeEach(() => {
        store.user = {id: 2, role: 'teacher'}
    })

    it('redirects /login to teacher home', async () => {
        expect(await navigationGuard(route('/login'))).toBe('/teacher')
    })

    it('allows own role route', async () => {
        expect(await navigationGuard(route('/teacher/categories', {meta: {allowed_role: 'teacher'}}))).toBe(true)
    })

    it('redirects admin route to teacher home', async () => {
        expect(await navigationGuard(route('/admin/teachers', {meta: {allowed_role: 'admin'}}))).toBe('/teacher')
    })

    it('redirects unmatched route to teacher home', async () => {
        expect(await navigationGuard(route('/nonexistent', {matched: []}))).toBe('/teacher')
    })
})

describe('logged in as admin', () => {
    beforeEach(() => {
        store.user = {id: 3, role: 'admin'}
    })

    it('allows own role route', async () => {
        expect(await navigationGuard(route('/admin/teachers', {meta: {allowed_role: 'admin'}}))).toBe(true)
    })

    it('redirects teacher route to admin home', async () => {
        expect(await navigationGuard(route('/teacher/categories', {meta: {allowed_role: 'teacher'}}))).toBe('/admin')
    })
})
