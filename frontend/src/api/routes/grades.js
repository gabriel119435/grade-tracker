import {request} from '../request.js'

// examples: upsert_grades [{subcategory_id: 3, value: 7.5}], delete_grade_ids [12, 45]
export async function saveGrades(student_id, date, upsert_grades, delete_grade_ids) {
    return request('/api/grades', {
        method: 'POST',
        body: JSON.stringify({student_id, date, upsert_grades, delete_grade_ids})
    })
}

export async function getGrades(studentId, limit = null) {
    const url = limit ? `/api/students/${studentId}/grades?limit=${limit}` : `/api/students/${studentId}/grades`
    return request(url)
}
