from app import db

class TeacherInfo(db.Model):
    __tablename__ = 'teacher_info'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    department = db.Column(db.String(100))

    user = db.relationship('User', back_populates='teacher_info')