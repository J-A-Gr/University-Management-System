from app.extensions import db

class TeacherInfo(db.Model):
    __tablename__ = 'teacher_info'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'))  # TODO: grąžinti ForeignKey kai bus sukurtas Faculty modelis

    user = db.relationship('User', back_populates='teacher_info')
    # faculty = db.relationship('Faculty', back_populates='teachers')  # TODO

    # taught_modules = db.relationship('Module', back_populates='teacher')  # TODO Dėstytojai gali kurti ir redaguoti modulius, turi matyti savo modelius, 



def get_current_modules(self, semester=None):
        """Get modules currently taught by teacher"""
        try:
            query = self.taught_modules         # išsitraukia modulius, kuriuos dėstytojas moko
            if semester:
                query = query.filter_by(semester=semester) # jei nurodytas semestras, filtruojame pagal jį
            return query.all() 
        except Exception as e:
            raise Exception(f"Failed to get current modules: {str(e)}") #  grąžina klaidą, jei nepavyksta gauti modulių
        
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
    
    
def __repr__(self):
        faculty_name = self.faculty.name if self.faculty else "No Faculty"
        return f'<TeacherInfo ID:{self.id} - {self.user.full_name if self.user else "Unknown"} ({faculty_name})>'