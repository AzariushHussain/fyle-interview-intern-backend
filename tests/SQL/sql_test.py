import pytest
import random
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core import db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

TEST_DATABASE_URL = "sqlite:///:memory:"  

@pytest.fixture(scope='module')
def test_db():
    engine = create_engine(TEST_DATABASE_URL)

    from core.models.assignments import Assignment
    from core.models.users import User 
    from core.models.teachers import Teacher 
    from core.models.students import Student  

    db.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db.session = TestingSessionLocal()

    teacher1 = Teacher(id=1)  
    teacher2 = Teacher(id=2) 
    student = Student(id=1)  
    db.session.add_all([teacher1, teacher2, student])
    db.session.commit()

    yield db.session  

    db.session.close()  
    db.metadata.drop_all(engine)  


import logging

def create_n_graded_assignments_for_teacher(session, number: int = 0, teacher_id: int = 1) -> int:
    # Count the existing assignments with grade 'A' for the specified teacher
    grade_a_counter: int = session.query(Assignment).filter(
        Assignment.teacher_id == teacher_id,
        Assignment.grade == GradeEnum.A
    ).count()

    # Create 'n' graded assignments
    for _ in range(number):
        # Randomly select a grade from GradeEnum
        grade = random.choice(list(GradeEnum))
        logging.debug(f"Creating assignment with grade: {grade}")

        # Create a new Assignment instance
        assignment = Assignment(
            teacher_id=teacher_id,
            student_id=1,
            grade=grade,
            content='test content',
            state=AssignmentStateEnum.GRADED
        )

        # Add the assignment to the session
        session.add(assignment)

        # Update the grade_a_counter if the grade is 'A'
        if grade == GradeEnum.A:
            grade_a_counter += 1

    # Commit changes to the database
    session.commit()

    # Return the count of assignments with grade 'A'
    return grade_a_counter



def test_get_assignments_in_graded_state_for_each_student():
    """Test to get graded assignments for each student"""

    # Find all the assignments for student 1 and change its state to 'GRADED'
    submitted_assignments: Assignment = Assignment.filter(Assignment.student_id == 1)

    # Iterate over each assignment and update its state
    for assignment in submitted_assignments:
        assignment.state = AssignmentStateEnum.GRADED  # Or any other desired state

    # Flush the changes to the database session
    db.session.flush()
    # Commit the changes to the database
    db.session.commit()

    # Define the expected result before any changes
    expected_result = [(1, 3)]

    # Execute the SQL query and compare the result with the expected result
    with open('tests/SQL/number_of_graded_assignments_for_each_student.sql', encoding='utf8') as fo:
        sql = fo.read()

    # Execute the SQL query compare the result with the expected result
    sql_result = db.session.execute(text(sql)).fetchall()
    for itr, result in enumerate(expected_result):
        assert result[0] == sql_result[itr][0]


def test_get_grade_A_assignments_for_teacher_with_max_grading(test_db):
    """Test to get count of grade A assignments for teacher which has graded maximum assignments"""

    # Read the SQL query from a file (this part remains unchanged)
    with open('tests/SQL/count_grade_A_assignments_by_teacher_with_max_grading.sql', encoding='utf8') as fo:
        sql = fo.read()

    # Create and grade 5 assignments for the default teacher (teacher_id=1)
    grade_a_count_1 = create_n_graded_assignments_for_teacher(test_db, 5)

    # Execute the SQL query and check if the count matches the created assignments
    sql_result = test_db.execute(text(sql)).fetchall()
    assert grade_a_count_1 == sql_result[0][0]

    # Create and grade 10 assignments for a different teacher (teacher_id=2)
    grade_a_count_2 = create_n_graded_assignments_for_teacher(test_db, 10, 2)

    # Execute the SQL query again and check if the count matches the newly created assignments
    sql_result = test_db.execute(text(sql)).fetchall()
    assert grade_a_count_2 == sql_result[0][0]