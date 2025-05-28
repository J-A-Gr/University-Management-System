from app.extensions import db
from datetime import datetime

class Assessment(db.Model):
    """Assessment model - represents exams, assignments, tests"""
    __tablename__ = 'assessments'
    

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)  
    description = db.Column(db.Text) 
    due_date = db.Column(db.DateTime, nullable=False)  # 
    assessment_type = db.Column(db.Enum('egzaminas', 'uzduotis', 'testas', 'laboratorinis'), nullable=False)
    max_points = db.Column(db.Integer, nullable=False)  # 
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)  
    created_by_teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_info.id'), nullable=False)  
    

    module = db.relationship('Module', back_populates='assessments')  # Vienas modulis - daug assessments
    created_by_teacher = db.relationship('TeacherInfo', back_populates='created_assessments') 

    def __repr__(self):
        return f'<Assessment {self.title} ({self.assessment_type})>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'assessment_type': str(self.assessment_type) if self.assessment_type else None,
            'max_points': self.max_points,
            'is_active': self.is_active,
            'module_name': self.module.name if self.module else None,
            'module_id': self.module_id,
            'created_by_teacher_name': f"{self.created_by_teacher.user.first_name} {self.created_by_teacher.user.last_name}" if self.created_by_teacher and self.created_by_teacher.user else None
        }
    
    def validate_assessment_data(self):
        """Validate assessment data"""
        errors = []
        
        if not self.title or len(self.title.strip()) < 3:
            errors.append("Assessment title must be at least 3 characters long")
        
        if self.max_points <= 0:
            errors.append("Max points must be positive")
        
        if self.due_date and self.due_date < datetime.now():
            errors.append("Due date cannot be in the past")
        
        if not self.assessment_type:
            errors.append("Assessment type is required")
        
        return errors
    

