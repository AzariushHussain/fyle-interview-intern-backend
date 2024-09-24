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
        'teacher_id': 2 
    }
    response = client.post('/student/assignments/submit', json=submit_payload, headers=h_student_1)
    assert response.status_code == 200, f"Failed to submit assignment: {response.json}"

    submitted_assignment_id = response.json['data']['id']

    return [draft_assignment_id, submitted_assignment_id]



def test_get_assignments_student_1(client, h_student_1):
    response = client.get(
        '/student/assignments',
        headers=h_student_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 1


def test_get_assignments_student_2(client, h_student_2):
    response = client.get(
        '/student/assignments',
        headers=h_student_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 2


def test_post_assignment_null_content(client, h_student_1):
    """
    failure case: content cannot be null
    """

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': None
        })

    assert response.status_code == 400


def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None




def test_submit_assignment_student_1(client, h_student_1, setup_assignment):
    assignment_id = setup_assignment[0]

    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': assignment_id,
            'teacher_id': 2  
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2


def test_assignment_resubmit_error(client, h_student_1, setup_assignment):
    assignment_id = setup_assignment[1]

    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': assignment_id,
            'teacher_id': 2  
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'assignment cannot be resubmitted'
