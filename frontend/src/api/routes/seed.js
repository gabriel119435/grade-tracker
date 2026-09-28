import {request} from '../request.js'

export async function seedDatabase() {
    return request('/api/admin/seed', {method: 'POST'})
}
