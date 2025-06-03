from app.extensions import db
from datetime import datetime


class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.Enum('pirmadienis', 'antradienis', 'trečiadienis', 'ketvirtadienis', 'penktadienis'), nullable=False) #kokia diena vyks paskaita
    semester = db.Column(db.Enum('rudens', 'pavasario'), nullable=False) # nusirodom kuriam semestre modulis destomas
    start_time = db.Column(db.Time, nullable=False) #Paskaitos pradžios laikas
    end_time = db.Column(db.Time, nullable=False) #Paskaitos pabaigos laikas
    room = db.Column(db.String(50))  # Auditorijos numeris, kad studentas žinotų kur vyks paskaita
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Modulių (kursų) kūrimo, redagavimo, peržiūros ir ištrynimo operacijos.
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # šito gal ir nelabai reikia, bet gal statistikai pravers	Sistemos būklė: Rodyti statistinę informaciją (vartotojų, modulių, studijų programų, grupių skaičius).
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    study_program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher_info.id'), nullable=False)

    teacher = db.relationship('TeacherInfo', back_populates='taught_modules')
    created_by = db.relationship('User', back_populates='created_modules')# sito reikia, kad zinotume kas ir ka sukure
    study_program = db.relationship('StudyProgram', back_populates='modules')# sito reiks. . . visur :D
    assessments = db.relationship('Assessment', back_populates='module')
    enrollments = db.relationship('ModuleEnrollment', back_populates='module', cascade='all, delete-orphan')    
    prerequisite_records = db.relationship('ModulePrerequisite', foreign_keys='ModulePrerequisite.module_id', back_populates='module')
    required_for_records = db.relationship('ModulePrerequisite', foreign_keys='ModulePrerequisite.prerequisite_id', back_populates='prerequisite_module')
    tests = db.relationship('Test', back_populates='module')

    attendance_records = db.relationship('AttendanceRecord', back_populates='module', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Module {self.name}>'
    
    def to_dict(self):   # 
        """Converts model to dictionary""" 
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'credits': self.credits,
            'semester': self.semester,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'room': self.room,
            'is_active': self.is_active,
            'study_program_name': self.study_program.name if self.study_program else None,
            'teacher_name': f"{self.teacher.user.first_name} {self.teacher.user.last_name}" if self.teacher and self.teacher.user else None,  #destyti gali kitas destytojas nei tas, kuris sukure moduli
            'created_by_name': f"{self.created_by.first_name} {self.created_by.last_name}" if self.created_by else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'prerequisites': self.get_prerequisites_list(),
            'has_prerequisites': self.has_prerequisites(),
            'prerequisite_count': len(self.get_prerequisites())
        }
       



    @staticmethod
    def get_active_modules(): #cia gal adminui reiks :D is tikruju tai padariau def get_modules_by_program(program_id): is suabejojau ar sito bereikia :D
        """Return all active modules"""
        return Module.query.filter_by(is_active=True).all()
    
    @staticmethod    # 
    def get_modules_by_program(program_id):   # gaunam studiju programos aktyvius modulius, o studentas gali rinktis moduli is savo studiju programos modeliu.
        """Returns modules by study program"""
        return Module.query.filter_by(study_program_id=program_id, is_active=True).all()

    @staticmethod    # 
    def get_student_available_modules(
        program_id,
        semester,
        available_credits,
        ):   # gaunam tik tuos modulius, kuriuos gali rinktis studentas.
        """Returns modules by study program"""
        return Module.query.filter(
            Module.study_program_id == program_id,
            Module.is_active == True,
            Module.semester == semester,
            Module.credits < available_credits 
            ).all() # 

    def soft_delete(self):
        """Soft delete module - marks as inactive instead of permanent deletion"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    

    def validate_time_conflict(self, study_program_id=None):   # TODO prie studetu registracijos i modulius, reiks patikrinti ar nesikerta su kitais moduliais
        """Checks for time conflicts with other modules in the same study program"""
        query = Module.query.filter(
            Module.id != self.id,
            Module.is_active == True,
            Module.day_of_week == self.day_of_week,
            Module.start_time < self.end_time,
            Module.end_time > self.start_time
        )
        
        if study_program_id:
            query = query.filter(Module.study_program_id == study_program_id)
        
        conflicting_modules = query.all()
        return conflicting_modules
    


    def get_prerequisites(self):
        """Get prerequisite modules for this module"""
        try:
            from app.models.module_prerequisite import ModulePrerequisite
            return ModulePrerequisite.get_module_prerequisites(self.id)
        except Exception as e:
            return []
    
    def get_required_for(self):
        """Get modules that require this module as prerequisite"""
        try:
            from app.models.module_prerequisite import ModulePrerequisite
            return ModulePrerequisite.get_modules_requiring(self.id)
        except Exception as e:
            return []
    
    def add_prerequisite(self, prerequisite_module_id):
        """Add a prerequisite module"""
        try:
            from app.models.module_prerequisite import ModulePrerequisite
            return ModulePrerequisite.create_prerequisite(self.id, prerequisite_module_id)
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def remove_prerequisite(self, prerequisite_module_id):
        """Remove a prerequisite module"""
        try:
            from app.models.module_prerequisite import ModulePrerequisite
            return ModulePrerequisite.remove_prerequisite(self.id, prerequisite_module_id)
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def check_student_prerequisites(self, student_id):
        """Check if student meets prerequisites for this module"""
        try:
            from app.models.module_prerequisite import ModulePrerequisite
            return ModulePrerequisite.check_student_can_enroll(student_id, self.id)
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_prerequisites_list(self):
        """Get prerequisites as dictionary list"""
        try:
            prerequisite_modules = self.get_prerequisites()
            return [
                {
                    'id': module.id,
                    'name': module.name,
                    'credits': module.credits,
                    'semester': module.semester
                }
                for module in prerequisite_modules
            ]
        except Exception as e:
            return []
    
    def has_prerequisites(self):
        """Check if module has any prerequisites"""
        return len(self.get_prerequisites()) > 0