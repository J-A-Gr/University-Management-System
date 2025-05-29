from app.extensions import db
from datetime import datetime

class AssessmentSubmission(db.Model):
    """AssessmentSubmission model - student submissions for assessments"""
    __tablename__ = 'assessment_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    grade = db.Column(db.Integer, nullable=True)  # Pažymys - gali būti None jei dar neįvertinta
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)  # Kada studentas pateikė
    comments = db.Column(db.Text)  # Dėstytojo komentarai
    
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # kad zinotume kam pazymi rasyti
    graded_by_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_info.id'), nullable=True)  # kas ivertino


    assessment = db.relationship('Assessment', back_populates='submissions')
    student = db.relationship('User', back_populates='submissions') 
    graded_by_teacher = db.relationship('TeacherInfo', back_populates='graded_submissions')


    __table_args__ = (
        db.CheckConstraint('grade >= 0', name='non_negative_grade'),  # uzsitikrinam kad nebutu neigiamu pazymiu
        db.UniqueConstraint('assessment_id', 'student_id', name='unique_submission_per_student'),  # neleidzia studentui atsiskaityti ta pati egza kelis kartus
    )

    def __repr__(self):
        return f'<AssessmentSubmission Student:{self.student_id} Assessment:{self.assessment_id} Grade:{self.grade}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'grade': self.grade,
            'comments': self.comments,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'assessment_id': self.assessment_id,
            'assessment_title': self.assessment.title if self.assessment else None,
            'student_id': self.student_id,
            'student_name': f"{self.student.first_name} {self.student.last_name}" if self.student else None,
            'graded_by_teacher_name': f"{self.graded_by_teacher.user.first_name} {self.graded_by_teacher.user.last_name}" if self.graded_by_teacher and self.graded_by_teacher.user else None
        }
    

    def is_graded(self):
        """Check if submission is graded"""
        return self.grade is not None
    
    def grade_submission(self, grade, teacher_id, comments=None):
        """Grade the submission"""
        try:
            if grade < 0:   #pasitikrinam ar nera minusiniu balu
                raise ValueError("Grade cannot be negative")
            
            if self.assessment and grade > self.assessment.max_points:  # pasitikrinam ar nera daugau uz max (11 in 10)
                raise ValueError(f"Grade cannot exceed max points ({self.assessment.max_points})")
            
            self.grade = grade
            self.graded_by_teacher_id = teacher_id
            
            if comments:
                self.comments = comments
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to grade submission: {str(e)}")

    def validate_submission_data(self):
        """Validate submission data"""
        errors = []
        
        if not self.assessment_id:
            errors.append("Assessment ID is required")
        
        if not self.student_id:
            errors.append("Student ID is required")
        
        return errors