import pytest

@pytest.fixture(scope='function')
def setup_assignment(client, h_student_1):
    create_assignment_payload_1 = {
        'content': "First assignment "
    }
    response = client.post('/student/assignments', json=create_assignment_payload_1, headers=h_student_1)
    assert response.status_code == 200, f"Failed to create first draft assignment: {response.json}"
    
    draft_assignment_id = response.json['data']['id']

    create_assignment_payload_2 = {
        'content': "Second assignment to submit"
    }
    response = client.post('/student/assignments', json=create_assignment_payload_2, headers=h_student_1)
    assert response.status_code == 200, f"Failed to create second draft assignment: {response.json}"
    
    to_submit_assignment_id = response.json['data']['id']

    submit_payload = {
        'id': to_submit_assignment_id,
        'teacher_id': 1
    }
    response = client.post('/student/assignments/submit', json=submit_payload, headers=h_student_1)
    assert response.status_code == 200, f"Failed to submit assignment: {response.json}"

    submitted_assignment_id = response.json['data']['id']

    return [draft_assignment_id, submitted_assignment_id]

def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']


def test_grade_assignment_cross(client, h_teacher_2, setup_assignment):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    assignment_id = setup_assignment[1]

    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": assignment_id,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": "A"
        }
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_draft_assignment(client, h_teacher_1, setup_assignment):
    """
    failure case: only a submitted assignment can be graded
    """
    assignment_id = setup_assignment[0]

    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": assignment_id,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'
