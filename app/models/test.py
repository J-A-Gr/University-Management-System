from app.extensions import db
from datetime import datetime
from app.models.test_result import TestResult 


class Test(db.Model):
    """Test model"""
    __tablename__ = 'tests'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    max_attempts = db.Column(db.Integer, default=1)
    show_results_immediately = db.Column(db.Boolean, default=True)  # ar rodyti rezultatus iš karto
    time_limit = db.Column(db.Integer, nullable=True)  # Laiko limitas minutėmis
    stop_after_pass = db.Column(db.Boolean, default=True)  # baigiasi bandymai, kai gauna teigiama bala


    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=True)
    created_by_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_info.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    

    module = db.relationship('Module', back_populates='tests')
    assessment = db.relationship('Assessment', back_populates='tests')
    created_by_teacher = db.relationship('TeacherInfo', back_populates='created_tests')
    test_questions = db.relationship('TestQuestion', back_populates='test', cascade='all, delete-orphan')
    test_results = db.relationship('TestResult', back_populates='test', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Test {self.title}>'
    

    def validate_test_settings(self):
            """Validate test configuration - CORE REQUIREMENT"""
            errors = []
            
            if not self.title or len(self.title.strip()) < 3:
                errors.append("Test title must be at least 3 characters long")
            
            if self.time_limit is not None and self.time_limit < 1:
                errors.append("Time limit must be at least 1 minute")
            
            if self.max_attempts < 1:
                errors.append("Maximum attempts must be at least 1")
            
            if not self.test_questions:
                errors.append("Test must have at least one question")
            else:
                total_points = sum(q.points for q in self.test_questions)
                if total_points == 0:
                    errors.append("Test must have points assigned to questions")
            
            if not self.module_id:
                errors.append("Test must be assigned to a module")
            
            return errors

    def is_ready_for_students(self):
        """Check if test is ready - CORE REQUIREMENT"""
        return self.is_active and len(self.validate_test_settings()) == 0



    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'time_limit': self.time_limit,
            'max_attempts': self.max_attempts,
            'is_active': self.is_active,
            'show_results_immediately': self.show_results_immediately,
            'module_name': self.module.name if self.module else None,
            'module_id': self.module_id,
            'assessment_title': self.assessment.title if self.assessment else None,
            'created_by_teacher_name': f"{self.created_by_teacher.user.first_name} {self.created_by_teacher.user.last_name}" if self.created_by_teacher and self.created_by_teacher.user else None,
            'questions_count': len(self.test_questions),
            'total_points': self.get_total_points(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    
    def get_total_points(self):
        """Get total points for the test"""
        try:
            return sum(q.points for q in self.test_questions)
        except Exception as e:
            return 0
        


    def can_student_take_test(self, student_id):
        """Check if student can take the test with comprehensive validation"""
        try:
            if not self.is_ready_for_students():  # Tikrinam ar testas yra paruoštas studentams
                return False, "Test is not ready for students"
            
            from app.models.module_enrollment import ModuleEnrollment # Tikrinam ar studentas užsiregistravęs į modulį
            from app.models.student_info import StudentInfo
            
            student_info = StudentInfo.query.filter_by(user_id=student_id).first() # ar turim toki studenta
            if not student_info:
                return False, "Student not found"
            
            enrollment = ModuleEnrollment.query.filter_by(  # ar studentas registravosi i moduli
                student_info_id=student_info.id,
                module_id=self.module_id,
                status='active'
            ).first()
            
            if not enrollment:
                return False, "You must be enrolled in the module to take this test"
            
            attempts = self.get_student_attempts(student_id) # tikrinam ar studentas turi aktyvių bandymų
            
            for attempt in attempts:
                if not attempt.is_completed():
                    return False, "You have an active attempt for this test. Please complete it before starting a new one."
            
            if self.stop_after_pass:  # jei testas baigiasi kai studentas gauna teigiamą pažymį
                for attempt in attempts: # tikrinam ar studentas jau turi teigiamą pažymį
                    if attempt.is_completed() and attempt.calculate_grade() >= 5:  # >= 5 = teigiamas
                        return False, "You already have a passing grade for this test"
            
            if len(attempts) >= self.max_attempts: # tikrinam ar studentas nepasiekė maksimalus bandymų skaičiaus
                return False, f"Maximum number of attempts reached ({self.max_attempts})"
            
            if not self.module.is_active:
                return False, "Module is not active, you cannot take the test"
            
            return True, "You can take the test"
            
        except Exception as e:
            return False, f"Error checking permissions: {str(e)}"
            

    def get_student_attempts(self, student_id):
        """Get student's attempts for this test"""
        try:
            return TestResult.query.filter_by(
                test_id=self.id,
                user_id=student_id
            ).order_by(TestResult.started_at.desc()).all()
        except Exception as e:
            return []


