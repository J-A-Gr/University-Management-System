from app import db

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)  # pvz., IFIN-18-A
    program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'))

    program = db.relationship('StudyProgram', back_populates='groups')
    students = db.relationship('StudentInfo', back_populates='group')