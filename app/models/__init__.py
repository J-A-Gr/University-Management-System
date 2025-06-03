from app.models.user import User
from app.models.student_info import StudentInfo
from app.models.teacher_info import TeacherInfo
from app.models.study_program import StudyProgram
from app.models.group import Group
from app.models.faculty import Faculty 
from app.models.module import Module
from app.models.assessment import Assessment
from app.models.assessment_submission import AssessmentSubmission
from app.models.module_enrollment import ModuleEnrollment
from app.models.module_prerequisite import ModulePrerequisite
from app.models.test import Test
from app.models.test_question import TestQuestion
from app.models.test_answer import TestAnswer   
from app.models.test_result import TestResult
from app.models.attendance_record import AttendanceRecord

__all__ = ['User', 'StudentInfo', 'TeacherInfo', 'StudyProgram', 'Group', 'Faculty', 'Module', 'Assessment', 'AssessmentSubmission', 'ModuleEnrollment', 'ModulePrerequisite', 'Test', 'TestQuestion', 'TestAnswer', 'TestResult', 'AttendanceRecord']