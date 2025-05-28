from app.extensions import db
from datetime import datetime 

class Faculty(db.Model):
    """Faculty model for organizing teachers and study programs (BONUS POINTS)"""
    __tablename__ = 'faculties'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(100), nullable=False, unique=True)  # "Informatikos fakultetas"
    code = db.Column(db.String(10), nullable=False, unique=True) 
    description = db.Column(db.Text) 
    is_active = db.Column(db.Boolean, default=True, nullable=False) #nesu tikra, kad reiks, bet gal adminas nores 'istrinti' faka? :D

    
    study_programs = db.relationship('StudyProgram', back_populates='faculty') 
    teachers = db.relationship('TeacherInfo', back_populates='faculty')


    def __repr__(self):
        return f'<Faculty {self.name} ({self.code})>'
    

    def create_faculty(name, code, description=None):
        """Create new faculty"""
        faculty = Faculty(name=name, code=code, description=description)
        db.session.add(faculty)
        db.session.commit()
        return faculty

    def to_dict(self): ###
        """Convert faculty to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'is_active': self.is_active,
            'study_programs_count': len(self.study_programs) if self.study_programs else 0,
            'teachers_count': len(self.teachers) if self.teachers else 0
        } 
    

    def activate(self):
        """Activate faculty"""
        self.is_active = True
        db.session.commit()

    def deactivate(self):
        """Soft delete faculty"""
        self.is_active = False
        db.session.commit()

    @staticmethod
    def get_active_faculties():
        """Get all active faculties"""
        return Faculty.query.filter_by(is_active=True).all()
    


