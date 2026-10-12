import {request} from '../request.js'

export async function login(username, password) {
    return request('/api/login', {method: 'POST', body: JSON.stringify({username, password})})
}

export async function logout() {
    return request('/api/logout', {method: 'POST'})
}

export async function changeAdminPassword(oldPassword, newPassword) {
    return request('/api/admin/password', {
        method: 'PATCH', body: JSON.stringify({old_password: oldPassword, new_password: newPassword})
    })
}

export async function setLocale(locale) {
    return request('/api/users/locale', {method: 'PATCH', body: JSON.stringify({locale})})
}

export async function getMe() {
    return request('/api/me')
}
