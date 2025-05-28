from app.extensions import db

class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)  # name = code? pvz., IFIN-18-A
    admission_year = db.Column(db.Integer, nullable=False) # student_info irgi yra admission_year, bet čia grupės admision_year, susitikrinti ar sutampa studentu istojimo laikas ir grupes kodas, ir kad galetume filtruoti grupes pagal metus (jeigu reiktu)
    group_letter = db.Column(db.String(1), nullable=False) # A, B, C,
    
    study_program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'), nullable=False) #viena grupė priklauso vienai studijų programai, bet viena studijų programa gali turėti daug grupių
    
    study_program = db.relationship('StudyProgram', back_populates='groups') #back_populates = 'groups' reiškia, kad StudyProgram modelyje bus ryšys su grupėmis
    students = db.relationship('StudentInfo', back_populates='group')


    @property               #susiskai2iuojam studentų kiekį, kad galetume formuoti grupę ()
    def student_count(self):
        """Get total number of students in this group"""
        return len(self.students)
    

    @property
    def is_full(self):    #grupės formavimui. jeigu virš 30, naujos grupės reikia?
        """Check if group is full (assuming max 30 students per group)"""
        return self.student_count >= 30
    
    
    
    ##########
    
    
    def add_student(self, student):
        """Add student to this group"""  
        try:
            if self.is_full:           # čia jeigu dar kažkokių validacijų sugalvotumėt, tai žinot kur kreiptis :D
                raise ValueError("Group is full (maximum 30 students)")
            
            if student.study_program_id != self.study_program_id:
                raise ValueError("Student must be in the same study program as group")
            
            if student.admission_year != self.admission_year:
                raise ValueError("Student admission year must match group admission year")
            
            student.group_id = self.id
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to add student to group: {str(e)}")
    
    def remove_student(self, student):
        """Remove student from this group"""
        try:
            if student.group_id == self.id:     #pasitikrinam ar studentas tikrai priklauso grupei
                student.group_id = None         #jeigu taip, tai spiriam lauk
                db.session.commit()
                return True
            else:
                return False, "Student not in this group"
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to remove student from group: {str(e)}")
    

    
    @staticmethod
    def create_group(study_program, admission_year, group_letter='A'):
        """Create new group with generated name (IFIN-23-A)"""
        try:
            group_name = 'IFIN-18-A' # TODO cia reiktu tureti sugeneruota studiju programos koda
#
            existing_group = Group.query.filter_by(name=group_name).first()  # pasicheckinam ar dar neturim tokios grupės
            if existing_group:
                raise ValueError(f"Group {group_name} already exists")
            
            new_group = Group(    # susikuriam naują grupę
                name=group_name,
                admission_year=admission_year,
                group_letter=group_letter,
                study_program_id=study_program.id   #susikuriam ryšį su studijų programa
            )
            
            db.session.add(new_group)
            db.session.commit()
            return new_group
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create group: {str(e)}")
    # TODO atsizymeti veliau :D
    # def __repr__(self):
    #     return f'<Group {self.name} - {self.study_program.name} - {self.student_count} students>'

    # program = db.relationship('StudyProgram', back_populates='groups') # TODO patikrinti ryšį
