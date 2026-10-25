import {request} from '../request.js'

// public, no login needed: [{id: 1, name: 'arena'}], sorted by name, fills the login picker
export async function getArenas() {
    return request('/api/arenas')
}
