from datetime import datetime
from app.extensions import db

class StudentInfo(db.Model):
    """Student information"""
    __tablename__ = 'student_info'
    
    id = db.Column(db.Integer, primary_key=True)
    admission_year = db.Column(db.Integer, nullable=False)  # Įstojimo metai
    current_semester = db.Column(db.Integer, default=1)    # Dabartinis semestras
    completed_credits = db.Column(db.Integer, default=0)   # Surinkti kreditai
    
    # Ryšiai su kitais modeliais
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    study_program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    
    # Ryšiai
    user = db.relationship('User', back_populates='student_info') #back_populates = 'student_info' reiškia, kad User modelyje bus ryšys su student_info
    study_program = db.relationship('StudyProgram', back_populates='students')
    group = db.relationship('Group', back_populates='students')
    #Ryšiai su moduliais ir pažymiais
    module_enrollments = db.relationship('ModuleEnrollment', back_populates='student_info')
    
    @property
    def year_of_study(self):
        """Calculate current year of study"""
        return ((self.current_semester - 1) // 2) + 1
    

    # Išsiaiškinam koks semestras
    @property
    def is_fall_semester(self):
        """Check if current semester is fall (odd numbers)"""
        return self.current_semester % 2 == 1
    
    @property
    def is_spring_semester(self):
        """Check if current semester is spring (even numbers)"""
        return self.current_semester % 2 == 0
    
    def advance_semester(self):
        """Advance to next semester"""
        try:
            self.current_semester += 1          # padidina semestro numerį
            self.updated_at = datetime.utcnow()
            db.session.commit()
        except Exception as e:
            db.session.rollback()               # esant kalidai, atkuria pradinę būsena
            raise Exception(f"Failed to advance semester: {str(e)}")
    
    def add_credits(self, credits):
        """Add completed credits"""
        try:
            if credits < 0:
                raise ValueError("Credits cannot be negative")
            self.completed_credits += credits
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to add credits: {str(e)}")
    

    #sužinom visus modulius, kur studentas yra uzsiregistravęs, naudosim studento profilyje, tvarkaraštyje, modulių konfliktų tikrinime, 
    def get_enrolled_modules(self, semester=None):
        """Get modules student is enrolled in for specific semester"""
        try:
            query = self.module_enrollments
            if semester:
                query = query.filter_by(semester=semester)
            return query.all()
        except Exception as e:
            raise Exception(f"Failed to get enrolled modules: {str(e)}")
        

    
    # Pasitikrinam ar studentas nėra užsiregistravęs konkrečiame modulyje, registracijoj tikrinsim ar dar nėra užsireginęs į modulį, 
    def is_enrolled_in_module(self, module_id, semester=None):
        """Check if student is enrolled in specific module"""
        try:
            query = self.module_enrollments.filter_by(module_id=module_id)
            if semester:
                query = query.filter_by(semester=semester)
            return query.first() is not None
        except Exception as e:
            raise Exception(f"Failed to check module enrollment: {str(e)}")
    

    #  "Stebima studentų pažanga" - ...
    def calculate_gpa(self):
        """Calculate Grade Point Average"""
        try:
            total_points = 0
            total_credits = 0
            
            for enrollment in self.module_enrollments:
                if enrollment.final_grade and enrollment.final_grade > 0:
                    total_points += enrollment.final_grade * enrollment.module.credits
                    total_credits += enrollment.module.credits
            
            if total_credits == 0:
                return 0.0
            
            return round(total_points / total_credits, 2)
        except Exception as e:
            raise Exception(f"Failed to calculate GPA: {str(e)}")
    
    
    def __repr__(self):
        return f'<StudentInfo ID:{self.id} - {self.user.full_name if self.user else "Unknown"}>'