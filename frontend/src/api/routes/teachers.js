import {request} from '../request.js'

export async function getTeachers() {
    return request('/api/teachers')
}

export async function createTeacher(username, password) {
    return request('/api/teachers', {
        method: 'POST', body: JSON.stringify({username, password})
    })
}

export async function deleteTeacher(id) {
    return request(`/api/teachers/${id}`, {method: 'DELETE'})
}
