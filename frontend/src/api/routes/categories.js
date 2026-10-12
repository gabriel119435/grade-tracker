import {request} from '../request.js'

export async function getCategories() {
    return request('/api/categories')
}

export async function createCategory(name) {
    return request('/api/categories', {method: 'POST', body: JSON.stringify({name})})
}

export async function deleteCategory(id) {
    return request(`/api/categories/${id}`, {method: 'DELETE'})
}

export async function createSubcategory(name, categoryId) {
    return request('/api/subcategories', {method: 'POST', body: JSON.stringify({name, category_id: categoryId})})
}

export async function deleteSubcategory(id) {
    return request(`/api/subcategories/${id}`, {method: 'DELETE'})
}
