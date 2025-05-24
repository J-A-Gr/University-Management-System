from app import db

class StudyProgram(db.Model):
    __tablename__ = 'study_programs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    faculty = db.Column(db.String(100), nullable=False)

    groups = db.relationship('Group', back_populates='program')
    students = db.relationship('StudentInfo', back_populates='program')