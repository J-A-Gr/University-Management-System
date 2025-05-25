from app.extensions import db

class StudentInfo(db.Model):
    __tablename__ = 'student_info'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))
    program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'))

    user = db.relationship('User', back_populates='student_info')
    program = db.relationship('StudyProgram', back_populates='students')
    group = db.relationship('Group', back_populates='students')