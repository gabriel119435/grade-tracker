def login(client, username, password):
    client.post('/api/login', json={'username': username, 'password': password})


def test_upsert_creates_grade(client, grade_context):
    login(client, 'teacher1', grade_context['password'])
    res = client.post('/api/grades', json={
        'student_id': grade_context['student1_id'],
        'date': '2024-01-15',
        'upsert_grades': [{'subcategory_id': grade_context['subcategory1_id'], 'value': 8.5}],
    })
    assert res.status_code == 201
    assert res.get_json() == {'message': 'saved'}


def test_upsert_updates_existing_grade(client, grade_context):
    login(client, 'teacher1', grade_context['password'])
    payload = {
        'student_id': grade_context['student1_id'],
        'date': '2024-01-15',
        'upsert_grades': [{'subcategory_id': grade_context['subcategory1_id'], 'value': 8.5}],
    }
    client.post('/api/grades', json=payload)

    payload['upsert_grades'][0]['value'] = 9.0
    res = client.post('/api/grades', json=payload)
    assert res.status_code == 201
    assert res.get_json() == {'message': 'saved'}

    grades = client.get(f"/api/students/{grade_context['student1_id']}/grades").get_json()
    assert grades[0]['subcategories'][0]['grades'][0]['value'] == 9.0


def test_upsert_rejects_value_out_of_range(client, grade_context):
    login(client, 'teacher1', grade_context['password'])
    res = client.post('/api/grades', json={
        'student_id': grade_context['student1_id'],
        'date': '2024-01-15',
        'upsert_grades': [{'subcategory_id': grade_context['subcategory1_id'], 'value': 11.0}],
    })
    assert res.status_code == 400
    assert res.get_json() == {'error': 'grade_out_of_range'}


def test_upsert_rejects_invalid_subcategory(client, grade_context):
    login(client, 'teacher1', grade_context['password'])
    res = client.post('/api/grades', json={
        'student_id': grade_context['student1_id'],
        'date': '2024-01-15',
        'upsert_grades': [{'subcategory_id': 99999, 'value': 8.0}],
    })
    assert res.status_code == 400
    assert res.get_json() == {'error': 'invalid_subcategory_id'}


def test_upsert_rejects_invalid_date(client, grade_context):
    login(client, 'teacher1', grade_context['password'])
    res = client.post('/api/grades', json={
        'student_id': grade_context['student1_id'],
        'date': 'not-a-date',
        'upsert_grades': [{'subcategory_id': grade_context['subcategory1_id'], 'value': 8.0}],
    })
    assert res.status_code == 400
    assert res.get_json() == {'error': 'invalid_date_format'}


def _create_grade(client, grade_context, teacher='teacher1', value=8.0):
    """creates a grade as the given teacher and returns its id"""
    login(client, teacher, grade_context['password'])
    client.post('/api/grades', json={
        'student_id': grade_context['student1_id'],
        'date': '2024-01-15',
        'upsert_grades': [{'subcategory_id': grade_context['subcategory1_id'], 'value': value}],
    })
    # fetch the grade id from the read endpoint
    res = client.get(f"/api/students/{grade_context['student1_id']}/grades")
    grade = res.get_json()[0]['subcategories'][0]['grades'][0]
    return grade['id']


def test_delete_removes_grade(client, grade_context):
    grade_id = _create_grade(client, grade_context)
    res = client.post('/api/grades', json={
        'student_id': grade_context['student1_id'],
        'delete_grade_ids': [grade_id],
    })
    assert res.status_code == 201
    assert res.get_json() == {'message': 'saved'}

    grades = client.get(f"/api/students/{grade_context['student1_id']}/grades").get_json()
    assert grades == []


def test_delete_forbidden_for_other_teacher(client, grade_context):
    # teacher1 creates a grade; teacher2 tries to delete it
    grade_id = _create_grade(client, grade_context, teacher='teacher1')
    login(client, 'teacher2', grade_context['password'])
    res = client.post('/api/grades', json={
        'student_id': grade_context['student1_id'],
        'delete_grade_ids': [grade_id],
    })
    assert res.status_code == 403
    assert res.get_json() == {'error': 'forbidden'}


def test_delete_rejects_nonexistent_grade(client, grade_context):
    login(client, 'teacher1', grade_context['password'])
    res = client.post('/api/grades', json={
        'student_id': grade_context['student1_id'],
        'delete_grade_ids': [99999],
    })
    assert res.status_code == 404
    assert res.get_json() == {'error': 'grades_not_found'}
