from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, bcrypt
import re

class User(UserMixin, db.Model):
    """User model for storing user related details"""
    __tablename__ = 'users'
    
    # išmečiau username, manau nereiktų studentams leisti kurtis usernameų, ypač pirmam kurse :D
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    birthday = db.Column(db.DateTime)

    profile_picture = db.Column(db.String(255), default='default.png') 
    # pridėtas identifikatorius user. (gali būti kaip pvz dėstytojas ir admin.)
    is_student = db.Column(db.Boolean, default=False)
    is_teacher = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

    is_active = db.Column(db.Boolean, default=True)
    
    failed_login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)


    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # pridėti ryšiai su student_info / teacher_info lentelėmis.
    student_info = db.relationship('StudentInfo', back_populates='user', uselist=False) # uselist=False užtikrina one-to-one ryšį.
    teacher_info = db.relationship('TeacherInfo', back_populates='user', uselist=False)
    created_modules = db.relationship('Module', back_populates='created_by')
    submissions = db.relationship('AssessmentSubmission', back_populates='student')
    test_results = db.relationship('TestResult', back_populates='user') # sita dedam cia, o ne pas student, kad destytojas ar adminas galetu irgi pabandyti issispresti/ prasitestuoti testa

    @property
    def full_name(self):
        """Get user's full name"""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


    # pasitikrinam kokia user rolė
    @property
    def role(self):
        """Get user's primary role"""
        if self.is_admin:
            return 'admin'
        elif self.is_teacher:
            return 'teacher'
        elif self.is_student:
            return 'student'
        return 'unknown'

    # dėl atvaizdavimo webe.
    @property
    def role_display(self):
        role_map = {
            'student': 'Studentas',
            'teacher': 'Dėstytojas',
            'admin': 'Administratorius'
        }
        return role_map.get(self.role, self.role)



    def set_password(self, password):
        """Set user's password"""
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        """Check user's password"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_locked(self):
        return self.locked_until and self.locked_until > datetime.utcnow()


    #•	5.2 Vartotojų Administravimas
    # Valdyti vartotojų vaidmenis bei priskyrimus prie studijų programų.
    def set_role(self, role):
        """Set user's primary role"""
        try:
            # Reset all roles
            self.is_student = False
            self.is_teacher = False
            self.is_admin = False
            
            # Set new role
            if role == 'student':
                self.is_student = True
            elif role == 'teacher':
                self.is_teacher = True
            elif role == 'admin':
                self.is_admin = True
            else:
                raise ValueError(f"Invalid role: {role}")
            
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to set role: {str(e)}")
    


    #	5.2 Vartotojų Administravimas
    # Valdyti vartotojų vaidmenis bei priskyrimus prie studijų programų.

    # Gražina studijų programos ID tiesiai iš vartotojo, jei vartotojas yra studentas ir turi studento informaciją.
    @property
    def study_id(self):
        if self.is_student and self.student_info:
            return self.student_info.study_program_id
        return None

    def change_study_program(self, new_program_id):
        """Change student's study program"""
        try:
            if not self.is_student or not self.student_info:
                raise ValueError("User is not a student")
            
            self.student_info.study_program_id = new_program_id
            # Galimai pagal nauja (pakesita studiju programą reiktų pasikeisti ir studento grupę)
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to change study program: {str(e)}")


    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
    
    def ensure_student_info(self):
        # Reikia pridėti "try"
        if self.is_student and not self.student_info:
            from app.models.student_info import StudentInfo
            self.student_info = StudentInfo(user_id=self.id)
            db.session.add(self.student_info)

    def ensure_teacher_info(self):
        if self.is_teacher and not self.teacher_info:
            from app.models.teacher_info import TeacherInfo
            self.teacher_info = TeacherInfo(user_id=self.id)
            db.session.add(self.teacher_info)
