-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
SELECT  COUNT(teacher_id) AS a_count,teacher_id
FROM assignments
WHERE state = 'GRADED' AND grade = 'A'
GROUP BY teacher_id
ORDER BY a_count DESC
LIMIT 1;
