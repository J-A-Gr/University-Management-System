from app.extensions import db
from datetime import datetime


class Module(db.Model):
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    credits = db.Column(db.Integer, nullable=False)
    day_of_week = db.Column(db.String(20)) #kokia diena vyks paskaita
    semester = db.Column(db.Enum('rudens', 'pavasario'), nullable=False) # nusirodom kuriam semestre modulis destomas
    start_time = db.Column(db.Time, nullable=False) #Paskaitos pradžios laikas
    end_time = db.Column(db.Time, nullable=False) #Paskaitos pabaigos laikas
    room = db.Column(db.String(50))  # Auditorijos numeris, kad studentas žinotų kur vyks paskaita
    is_active = db.Column(db.Boolean, default=True, nullable=False)  # Modulių (kursų) kūrimo, redagavimo, peržiūros ir ištrynimo operacijos.
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # šito gal ir nelabai reikia, bet gal statistikai pravers	Sistemos būklė: Rodyti statistinę informaciją (vartotojų, modulių, studijų programų, grupių skaičius).
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    study_program_id = db.Column(db.Integer, db.ForeignKey('study_programs.id'), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
    study_program = db.relationship('StudyProgram', backref='modules') # sito reiks. . . visur :D
    created_by = db.relationship('User', backref='created_modules')  # sito reikia, kad zinotume kas ir ka sukure
    
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
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'room': self.room,
            'is_active': self.is_active,
            # TODO pasiziureti biski dar kas cia ne taip :D
            # 'study_program_name': self.study_program.name if self.study_program else None,
            # 'created_by_name': f"{self.created_by.first_name} {self.created_by.last_name}" if self.created_by else None,
            # 'created_at': self.created_at.isoformat() if self.created_at else None
        }
       


       
    @staticmethod
    def get_active_modules(): #cia gal adminui reiks :D is tikruju tai padariau def get_modules_by_program(program_id): is suabejojau ar sito bereikia :D
        """Return all active modules"""
        return Module.query.filter_by(is_active=True).all()
    
    @staticmethod    # 
    def get_modules_by_program(program_id):   # gaunam studiju programos aktyvius modulius, o studentas gali rinktis moduli is savo studiju programos modeliu.
        """Returns modules by study program"""
        return Module.query.filter_by(study_program_id=program_id, is_active=True).all()
    
    def soft_delete(self):
        """Soft delete module - marks as inactive instead of permanent deletion"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def validate_time_conflict(self): # TODO prie studetu registracijos i modulius, reiks patikrinti ar nesikerta su kitais moduliais
        """Checks for time conflicts with other modules"""
        conflicting_modules = Module.query.filter(
            Module.id != self.id,
            Module.is_active == True,
            Module.day_of_week == self.day_of_week,
            Module.start_time < self.end_time,
            Module.end_time > self.start_time
        ).all()
        
        return conflicting_modules