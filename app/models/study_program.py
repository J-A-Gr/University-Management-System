from app.extensions import db

class StudyProgram(db.Model):
    """Study program model for organizing students and modules"""
    __tablename__ = 'study_programs'
    
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, unique=True)  # "Informatikos inžinerija"
    code = db.Column(db.String(10), nullable=False, unique=True)   # “IN” – informatikos programa “IFIN” – informatikos fako informatikos progr”

    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id'))  # programa priklauso fakui
    
    # Ryšiai

    faculty = db.relationship('Faculty', back_populates='study_programs') #back_populates = 'study_programs' reiškia, kad Faculty modelyje bus ryšys su studijų programomis
    students = db.relationship('StudentInfo', back_populates='study_program')
    groups = db.relationship('Group', back_populates='study_program')
    # logiskiau manau butu many to many su moduliais, nes viena programa gali turėti daug modulių, o vienas modulis gali priklausyti daugeliui programų - pritariu :)
    # bet dabar pasilikim prie vienai studiju programai priklauso daug moduliu.
    modules = db.relationship('Module', back_populates='study_program')

    # TODO pagal mane čia dar turėtų būti grupės kodo generavimas, bet kol kas palieku kaip yra, nes grupės kodas yra sudarytas iš programos kodo, fakulteto  ir metų

    # Programos kodo sugeneravimas
    def generate_code(self):
        try:
            self.code = self.name[:4].upper() #Pirmos keturios didžiosios raidės iš programos pavadinimo
            return self.code
        except Exception as e:
            raise Exception (f"Failed to generate study program code: {str(e)}")



    def student_count(self):
        """Get total number of students in this program"""
        return len(self.students)



    def get_students_by_year(self, admission_year): # tur4tų būti reikalinga grupės kodo sudarymui, jeigu ne tai istrinam ;D
        """Get students by admission year"""
        try:
            return [s for s in self.students if s.admission_year == admission_year]
        except Exception as e:
            raise Exception(f"Failed to get students by year: {str(e)}")
        



    def enroll_student(self, student):          # •	5.2 Vartotojų Administravimas Valdyti vartotojų vaidmenis bei priskyrimus prie studijų programų.
        """Enroll student in this program"""
        try:
            if student.study_program_id and student.study_program_id != self.id: #pasitikrinam ar studentas nera priskirtas kitai studiju programai
                raise ValueError("Student already enrolled in another program")
            
            student.study_program_id = self.id  # priskiriam studiju programai
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to enroll student: {str(e)}")
    

    def add_module(self, module):    
        """Add module to this study program (Many-to-Many)"""
        try:
            if module not in self.modules:
                self.modules.append(module)
                db.session.commit()
                return True
            else:
                return False, "Module already in this program"
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to add module to program: {str(e)}")
        

    def remove_module(self, module):
        """Remove module from this study program"""
        try:
            if module in self.modules:
                self.modules.remove(module)
                db.session.commit()
                return True
            else:
                return False, "Module not found in this program"
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to remove module from program: {str(e)}")
    

    def __repr__(self):
        faculty_name = self.faculty.name if self.faculty else "No Faculty"
        return f'<StudyProgram {self.code}: {self.name} ({faculty_name}) - {self.student_count} students, {len(self.modules)} modules>'
 