from app.extensions import db
from datetime import datetime



class ModuleEnrollment(db.Model):
    """Model for student enrollment in modules"""
    __tablename__ = 'module_enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_info_id = db.Column(db.Integer, db.ForeignKey('student_info.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)
    semester = db.Column(db.Enum('rudens', 'pavasario'), nullable=True)  
    status = db.Column(db.Enum('active', 'completed', 'failed', 'dropped'), default='active')
    final_grade = db.Column(db.Integer, nullable=True)   
    completion_date = db.Column(db.DateTime, nullable=True) # Data kada modulis baigtas

    student_info = db.relationship('StudentInfo', back_populates='module_enrollments')
    module = db.relationship('Module', back_populates='enrollments')
    
    # Kad studentas negalėtų registruotis į tą patį modulį du kartus
    __table_args__ = (
        db.UniqueConstraint('student_info_id', 'module_id', name='unique_student_module'),
        db.CheckConstraint('final_grade >= 1 AND final_grade <= 10', name='valid_grade_range'),
    )

    def __repr__(self):
        return f'<ModuleEnrollment Student:{self.student_info_id} Module:{self.module_id} Status:{self.status}>'

    def is_completed(self):
        """check if the module is completed"""
        return self.status == 'completed' and self.final_grade and self.final_grade >= 5
    
    def is_failed(self):
        """cheak if the module is failed"""
        return self.status == 'failed' or (self.final_grade and self.final_grade < 5)
    
    def is_active(self):
        """Check if the module is active"""
        return self.status == 'active'
    
    def mark_completed(self, grade, teacher_id=None):
        """Change module status to completed with a grade"""
        try:
            if grade < 1 or grade > 10:
                return False, "Grade must be between 1 and 10"
            
            self.final_grade = grade
            self.completion_date = datetime.utcnow()
            
            if grade >= 5:  # Lietuvoje 5+ = praėjęs
                self.status = 'completed'
                # Pridėti kreditus studentui
                if self.student_info:
                    self.student_info.completed_credits += self.module.credits
            else:
                self.status = 'failed'
            
            db.session.commit()
            return True, f"Module is marked {self.status} (grade: {grade})" 
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
    
    def drop_enrollment(self):
        """Drop the module enrollment"""
        try:
            self.status = 'dropped'
            db.session.commit()
            return True, "Successfully dropped the module"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"
    

    @staticmethod
    def register_student(student_id, module_id):
        """Registration of a student to a module"""
        from app.models.student_info import StudentInfo
        from app.models.module import Module
        
        try:
            student = StudentInfo.query.get(student_id)
            if not student:
                return False, "Student not found"
            
            module = Module.query.get(module_id)
            if not module:
                return False, "Module not found"
            
            # Tikrinam ar dar neregistruotas
            existing = ModuleEnrollment.query.filter_by(
                student_info_id=student_id,
                module_id=module_id
            ).first()
            
            if existing:
                return False, f"You are already registered for this module (status: {existing.status})"
            
            # Tikrinan studijų programą
            if student.study_program_id != module.study_program_id:
                return False, "This module does not belong to your study program"
            
            # Tikrinam tvarkaraščio konfliktus
            for enrollment in student.module_enrollments:
                if enrollment.status != 'active':  # Tikrinam tik aktyvius modulius
                    continue
                    
                other_module = enrollment.module
                
                # Ar ne ta pati diena
                if other_module.day_of_week == module.day_of_week:
                    if (other_module.start_time < module.end_time and
                        other_module.end_time > module.start_time):
                        return False, f"Schedule conflict with {other_module.name}"
            
            # Tikrinam prerequisite
            prereq_ok, prereq_msg = ModuleEnrollment.check_prerequisites(student_id, module_id)
            if not prereq_ok:
                return False, f"Prerequisite error: {prereq_msg}"
            
            # Jei viskas gerai - registruojam
            new_enrollment = ModuleEnrollment(
                student_info_id=student_id,
                module_id=module_id,
                semester=module.semester,
                status='active'  # Pradžioj 'active'
            )
            
            db.session.add(new_enrollment)
            db.session.commit()
            
            return True, "Successfully registered for the module"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Registration error: {str(e)}"
        

    @staticmethod
    def check_prerequisites(student_id, module_id):
        """check if a student meets the prerequisites for a module"""
        try:
            from app.models.module import Module
            
            module = Module.query.get(module_id)
            if not module:
                return False, "Module not found"
            
            return module.check_student_prerequisites(student_id)
            
        except Exception as e:
            return False, f"Error checking requirements: {str(e)}"