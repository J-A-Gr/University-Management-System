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
 
    student_info = db.relationship('StudentInfo', back_populates='module_enrollments')
    module = db.relationship('Module', back_populates='enrollments')
    
    # Kad studentas negalėtų registruotis į tą patį modulį du kartus
    __table_args__ = (
        db.UniqueConstraint('student_info_id', 'module_id', name='unique_student_module'),
    )
    
    @staticmethod
    def register_student(student_id, module_id):
        """Registruoti studentą į modulį - viena paprasta funkcija"""
        from app.models.student_info import StudentInfo
        from app.models.module import Module
        student = StudentInfo.query.get(student_id) # randam studenta
        if not student:
            return "Studentas nerastas"
        
        module = Module.query.get(module_id) # randa moduli
        if not module:
            return "Modulis nerastas"
        
        for enrollment in student.module_enrollments:  #tikrinam ar neprisiregistrves
            if enrollment.module_id == module_id:
                return "Jau esi registruotas šiame modulyje"
        
        if student.study_program_id != module.study_program_id: # tikrinam ar modulis tinka studento studiju programai
            return "Šis modulis nepriklauso jūsų studijų programai"
        
        for enrollment in student.module_enrollments: # tikrinam ar tvarkarastis ok
            other_module = enrollment.module
            
            # Jei ta pati diena
            if other_module.day_of_week == module.day_of_week: # ar diena ta pati

                if (other_module.start_time < module.end_time and # ar laikas persidengia
                    other_module.end_time > module.start_time):
                    return f"Tvarkaraščio konfliktas su {other_module.name}"
        

        new_enrollment = ModuleEnrollment(  #jeigu viskas ok, tai registruojam
            student_info_id=student_id,
            module_id=module_id
        )
        
        db.session.add(new_enrollment)
        db.session.commit()
        
        return "Sėkmingai registruotasi!"


    def __repr__(self):
        return f'<ModuleEnrollment Student:{self.student_info_id} Module:{self.module_id}>'