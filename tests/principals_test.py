import pytest
from core.models.assignments import AssignmentStateEnum, GradeEnum

@pytest.fixture(scope='function')
def setup_assignments(client, request):
    headers = {
        'X-Principal': '{"user_id": 2, "student_id": 2}'
    }

    draft_assignment_payload = {
        'content': "Draft assignment"
    }
    response = client.post('/student/assignments', json=draft_assignment_payload, headers=headers)
    assert response.status_code == 200, f"Failed to create draft assignment: {response.json}"
    draft_assignment_id = response.json['data']['id']

    to_submit_assignment_payload = {
        'content': "submitted assignment"
    }
    response = client.post('/student/assignments', json=to_submit_assignment_payload, headers=headers)
    assert response.status_code == 200, f"Failed to create draft assignment: {response.json}"
    to_submit_assignment_id = response.json['data']['id']

    submit_payload = {
        'id': to_submit_assignment_id,
        'teacher_id': 1 
    }
    response = client.post('/student/assignments/submit', json=submit_payload, headers=headers)
    assert response.status_code == 200, f"Failed to submit assignment: {response.json}"
    
    submitted_assignment_id = response.json['data']['id']

    grade_headers = {
        'X-Principal': '{"user_id": 3, "teacher_id": 1}'  
    }
    grade_payload = {
        'id': submitted_assignment_id,
        'grade': GradeEnum.A.value  
    }
    response = client.post('/teacher/assignments/grade', json=grade_payload, headers=grade_headers)
    assert response.status_code == 200, f"Failed to grade assignment: {response.json}"
    
    graded_assignment_id = response.json['data']['id']

    def teardown():
        client.delete(f'/assignments/{graded_assignment_id}', headers=grade_headers)

    request.addfinalizer(teardown)

    return [submitted_assignment_id, draft_assignment_id]




def test_get_assignments(client, h_principal, setup_assignments):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal, setup_assignments):
    """
    Failure case: If an assignment is in Draft state, it cannot be graded by principal.
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': setup_assignments[1],  
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400


def test_grade_assignment(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': setup_assignments[0],  
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C.value


def test_regrade_assignment(client, h_principal, setup_assignments):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': setup_assignments[0],  
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B.value


def test_get_teachers(client, h_principal):
    """Test to get all teachers' data."""
    
    response = client.get(
        '/principal/teachers',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']

    assert isinstance(data, list)

    for teacher in data:
        assert 'id' in teacher  
        assert 'created_at' in teacher  
        assert 'updated_at' in teacher  
