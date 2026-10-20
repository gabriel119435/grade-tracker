// 401 and 403 reaction, registered by main.js, keeps request.js free of router imports
let onSessionLost = () => {}

export function setSessionLostHandler(handler) {
    onSessionLost = handler
}

export async function request(url, options = {}) {
    let res

    try {
        const headers = options.body ? {'Content-Type': 'application/json', ...options.headers} : options.headers
        res = await fetch(url, {...options, headers})
    } catch (err) {
        console.error('network error:', err)
        return {error: 'network_error'}
    }

    // 401: session gone, 403: cookie belongs to another user than store.user, a tab left open across a login
    if ((res.status === 401 || res.status === 403) && url !== '/api/login') {
        await onSessionLost()
        return {error: res.status === 401 ? 'unauthorized' : 'forbidden'}
    }

    if (!res.ok) {
        const text = await res.text()
        try {
            const body = JSON.parse(text)
            if (body.error) return {error: body.error}
        } catch {
            // non-json body: falls through to invalid_response below
        }
        console.error('server error:', text)
        return {error: 'invalid_response'}
    }
    try {
        return await res.json()
    } catch (err) {
        console.error('server error:', err)
        return {error: 'invalid_response'}
    }
}
