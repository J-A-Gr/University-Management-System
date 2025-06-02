from app.extensions import db
from collections import defaultdict

class TeacherInfo(db.Model):
    __tablename__ = 'teacher_info'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'), nullable=True)  # TODO: grąžinti ForeignKey kai bus sukurtas Faculty modelis
    
    user = db.relationship('User', back_populates='teacher_info')
    taught_modules = db.relationship('Module', back_populates='teacher')   # TODO Dėstytojai gali kurti ir redaguoti modulius, turi matyti savo modelius, 
    faculty = db.relationship('Faculty', back_populates='teachers')  # TODO
    created_assessments = db.relationship('Assessment', back_populates='created_by_teacher')
    graded_submissions = db.relationship('AssessmentSubmission', back_populates='graded_by_teacher')
    created_tests = db.relationship('Test', back_populates='created_by_teacher')


    def get_current_modules(self, semester=None, is_active=True):
        """Get modules currently taught by teacher"""
        try:
            from app.models.module import Module 
            
            query = Module.query.filter_by(teacher_id=self.id)
            
            if is_active:
                query = query.filter_by(is_active=True)
            
            if semester:
                query = query.filter_by(semester=semester)
            
            return query.all()
        except Exception as e:
            raise Exception(f"Failed to get current modules: {str(e)}")
    


    def can_teach_in_faculty(self, faculty_id):
        """Check if teacher belongs to specific faculty"""
        return self.faculty_id == faculty_id # patikrina, ar dėstytojas priklauso fakultetui. Programoje įterpkite fakultetus Studentai ir moduliai privalo priklausyti konkrečiam fakultetui ir studijų programos priklauso fakultetui (pavyzdžiui Informatikos Inžinerija priklauso Informatikos fakultetui ) (Bonus points).



    def assign_module(self, module):
        """Assign a module to teacher with faculty validation"""
        try:
            if self.faculty_id and module.study_program and module.study_program.faculty_id:  # tikriname, ar dėstytojas priklauso fakui, ar modulis turi studiju programa, ar studiju programa priklauso fakui.
                if self.faculty_id != module.study_program.faculty_id: # jeigu dėstytojas priklauso kitam fakultetui negu modulis išmetam klaidą.
                    raise ValueError("Teacher cannot teach modules outside their faculty")
            
            module.teacher = self # prisiskiriam dėstytojq moduliui
            db.session.commit()
            return True 
        except Exception as e: #jeigu neiseina priskirti modulio, išmetam klaidą.
            db.session.rollback() # atsišaukiam sesija ir bandom laimę dar kartą :D bei bandom nesusisprogdinti smegenu :D
            raise Exception(f"Failed to assign module: {str(e)}")
        

    def remove_module(self, module):
        """Remove a module from teacher"""
        try:
            module.teacher = None # išstrinam moduli iš destytojo 
            db.session.commit()
            return True
        except Exception as e: 
            db.session.rollback() 
            raise Exception(f"Failed to remove module: {str(e)}")


    def to_dict(self):
        """Convert teacher info to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'faculty_id': self.faculty_id,
            'user_name': f"{self.user.first_name} {self.user.last_name}" if self.user else None,
            'user_email': self.user.email if self.user else None,
            'faculty_name': getattr(self.faculty, 'name', None) if hasattr(self, 'faculty') and self.faculty else None,
            'modules_count': len(self.get_current_modules()) if self.get_current_modules() else 0
        }
    

    
    def __repr__(self):
        faculty_name = self.faculty.name if self.faculty else "No Faculty"
        user_name = f"{self.user.first_name} {self.user.last_name}" if self.user else "Unknown"
        return f'<TeacherInfo ID:{self.id} - {user_name} ({faculty_name})>' 
    
    
    def get_schedule(self):
        schedule = defaultdict(list)

        for module in self.taught_modules:
            assessments_data = [
                {
                    "title": a.title,
                    "type": a.assessment_type,
                    "due_date": a.due_date.strftime("%Y-%m-%d")
                }
                for a in module.assessments if a.is_active
            ]

            schedule[module.day_of_week].append({
                "module_id": module.id,
                "module_name": module.name,
                "start_time": module.start_time.strftime("%H:%M"),
                "end_time": module.end_time.strftime("%H:%M"),
                "room": module.room,
                "assessments": assessments_data
            })

        return dict(schedule) 
