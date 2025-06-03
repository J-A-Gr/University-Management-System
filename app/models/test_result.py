from app.extensions import db
from datetime import datetime

class TestResult(db.Model):
    """Test result model for storing student test attempts"""
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer, default=0, nullable=False)
    max_possible_score = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.Enum('in_progress', 'completed', 'submitted'), default='in_progress', nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    time_taken = db.Column(db.Integer)  # sekundėmis
    
   
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
 
    test = db.relationship('Test', back_populates='test_results')
    user = db.relationship('User', back_populates='test_results')
    answers = db.relationship('TestAnswer', back_populates='test_result', cascade='all, delete-orphan')

    __table_args__ = (
        db.CheckConstraint('total_score >= 0', name='non_negative_score'),
        db.CheckConstraint('max_possible_score > 0', name='positive_max_score'),
        db.CheckConstraint('percentage >= 0 AND percentage <= 100', name='valid_percentage'),
    )

    def __repr__(self):
        return f'<TestResult {self.id}: User{self.user_id} Test{self.test_id} - {self.percentage}%>'

    @property
    def module(self):
        """Get module through assessment"""
        if self.test and self.test.assessment:
            return self.test.assessment.module
        return None

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'total_score': self.total_score,
            'max_possible_score': self.max_possible_score,
            'percentage': self.percentage,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_taken': self.time_taken,
            'test_id': self.test_id,
            'user_id': self.user_id
        }

    def calculate_score(self):
        """Calculate total score from answers"""
        try:
            total = 0
            for answer in self.answers:
                if answer.is_correct:
                    total += answer.question.points
            
            self.total_score = total
            self.percentage = (total / self.max_possible_score * 100) if self.max_possible_score > 0 else 0 
            return True
        except Exception as e:
            return False

    def is_completed(self):
        """Check if test attempt is completed"""
        return self.status == 'completed'

    def calculate_grade(self):
        """Calculate grade (1-10 scale) based on percentage"""
        if self.percentage >= 95: return 10
        elif self.percentage >= 85: return 9
        elif self.percentage >= 75: return 8
        elif self.percentage >= 65: return 7
        elif self.percentage >= 55: return 6
        elif self.percentage >= 45: return 5
        elif self.percentage >= 35: return 4
        elif self.percentage >= 25: return 3
        elif self.percentage >= 15: return 2
        else: return 1



    def complete_test(self):
        """Mark test as completed and calculate final score"""
        try:

            if self.status == 'completed': 
                return True, "Test already completed"

            self.completed_at = datetime.utcnow()
            self.status = 'completed'

            if self.started_at:
                time_difference = self.completed_at - self.started_at
                self.time_taken = int(time_difference.total_seconds())

            score_calculated = self.calculate_score()
            if not score_calculated:
                db.session.rollback()
                return False, "Error calculating final score"
            
            db.session.commit()
            return True, "Test completed successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error completing test: {str(e)}"
        
    
    def integrate_with_module_grade(self):
        """Integration per assessment"""
        try:
            from app.models.module_enrollment import ModuleEnrollment
            from app.models.assessment_submission import AssessmentSubmission
    
            if not self.user.student_info:
                return False, "Student info not found"
            
            if not self.test.assessment_id:
                return False, "Test is not linked to an assessment"
            
            assessment = self.test.assessment
            module = assessment.module
            
            enrollment = ModuleEnrollment.query.filter_by(
                student_info_id=self.user.student_info.id,
                module_id=module.id,
                status='active'
            ).first()
            
            if not enrollment:
                return False, "Student not enrolled in module"
        
            grade = self.calculate_grade()
            
            submission = AssessmentSubmission.query.filter_by(
                assessment_id=self.test.assessment_id,
                student_id=self.user.id
            ).first()
            
            if not submission:
                submission = AssessmentSubmission(
                    assessment_id=self.test.assessment_id,
                    student_id=self.user.id,
                    graded_by_teacher_id=self.test.created_by_teacher_id
                )
                db.session.add(submission)
            
            submission.grade = grade
            submission.comments = f"Automatiškai įvertinta iš testo. Rezultatas: {self.percentage:.1f}%"
            submission.submitted_at = self.completed_at
            
            if assessment.assessment_type == 'egzaminas' and grade >= 5:
                success, message = enrollment.mark_completed(grade)
                if success:
                    db.session.commit()
                    return True, f"Pažymys {grade} įrašytas. Modulis užbaigtas."
            
            db.session.commit()
            return True, f"Pažymys {grade} įrašytas atsiskaitymui '{assessment.title}'"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Integration error: {str(e)}"


    @staticmethod
    def get_user_results(user_id):
        """Get all test results for a specific user"""
        try:

            return TestResult.query.filter_by(user_id=user_id)\
                .order_by(TestResult.started_at.desc()).all() 
        except Exception as e:
            return []

    @staticmethod
    def get_test_statistics(test_id): 
        """Get statistics for a specific test"""
        try:
            results = TestResult.query.filter_by(test_id=test_id, status='completed').all()
            if not results:
                return None
            
            scores = [r.percentage for r in results]
            return {
                'total_attempts': len(results),
                'average_score': round(sum(scores) / len(scores), 1),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'pass_rate': round(len([s for s in scores if s >= 45]) / len(scores) * 100, 1)
            }
        except Exception as e:
            return None
        