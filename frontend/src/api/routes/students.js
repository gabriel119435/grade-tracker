import {request} from '../request.js'

export async function getStudents() {
    return request('/api/students')
}

export async function createStudent(username, password) {
    return request('/api/students', {
        method: 'POST', body: JSON.stringify({username, password})
    })
}

export async function deleteStudent(id) {
    return request(`/api/students/${id}`, {method: 'DELETE'})
}
