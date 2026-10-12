import {request} from '../request.js'

// ex: upsertGrades [{subcategory_id: 3, value: 7.5}], deleteGradeIds [12, 45]
export async function saveGrades(studentId, date, upsertGrades, deleteGradeIds) {
    return request('/api/grades', {
        method: 'POST',
        body: JSON.stringify({
            student_id: studentId,
            date,
            upsert_grades: upsertGrades,
            delete_grade_ids: deleteGradeIds,
        })
    })
}

// all grades from one student at one day {3: {id: 10, value: 7.5}} subcat-id 3 grade-id 10
export async function getDayGrades(studentId, date) {
    return request(`/api/students/${studentId}/grades/${date}`)
}

export async function getGrades(studentId, limit = null) {
    const query = limit ? `?limit=${limit}` : ''
    return request(`/api/students/${studentId}/grades${query}`)
}
