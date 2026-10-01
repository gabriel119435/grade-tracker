import router from '../router/index.js'
import {store} from '../store.js'

export async function request(url, options = {}) {
    let res

    try {
        const headers = options.body
            ? {'Content-Type': 'application/json', ...options.headers}
            : options.headers
        res = await fetch(url, {credentials: 'include', ...options, headers})
    } catch (err) {
        console.error(`network error:`, err)
        return {error: 'network_error'}
    }

    if (res.status === 401 && url !== '/api/login') {
        // session gone: forget the user, so the guard allows /login
        store.user = null
        await router.push('/login')
        return {error: 'unauthorized'}
    }
    if (!res.ok) {
        const text = await res.text()
        try {
            const body = JSON.parse(text)
            if (body.error) return {error: body.error}
        } catch {}
        console.error(`server error:`, text)
        return {error: 'invalid_response'}
    }
    try {
        return await res.json()
    } catch (err) {
        console.error(`server error:`, err)
        return {error: 'invalid_response'}
    }
}
