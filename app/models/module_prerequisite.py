from app.extensions import db

class ModulePrerequisite(db.Model):
    """Prerequisite relationships between modules"""
    __tablename__ = 'module_prerequisites'
    
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)


    
    module = db.relationship( # Modulis kuris turi prerequisite
        'Module', 
        foreign_keys=[module_id],
        back_populates='prerequisite_records'
    )
    
    prerequisite_module = db.relationship( # Modulis kuris yra prerequisite kitam
        'Module', 
        foreign_keys=[prerequisite_id],
        back_populates='required_for_records'
    )

    __table_args__ = ( #kad nesikartotų, kad modulis negali būti savo paties prerequisite
        db.UniqueConstraint('module_id', 'prerequisite_id', name='unique_prerequisite'),
    )

    def __repr__(self):
        return f'<ModulePrerequisite {self.module_id} requires {self.prerequisite_id}>'
    
    def to_dict(self):
        """Converts to dictionary"""
        return {
            'id': self.id,
            'module_id': self.module_id,
            'module_name': self.module.name if self.module else None,
            'prerequisite_id': self.prerequisite_id,
            'prerequisite_name': self.prerequisite_module.name if self.prerequisite_module else None
        }
    
    @staticmethod
    def create_prerequisite(module_id, prerequisite_id):
        """Create prerequisite relationship between modules"""
        try:
            if module_id == prerequisite_id:
                return False, "Module cannot be its own prerequisite"
            

            existing = ModulePrerequisite.query.filter_by(    # Tikrinti ar jau egzistuoja
                module_id=module_id,
                prerequisite_id=prerequisite_id
            ).first()
            
            if existing:
                return False, "Prerequisite relationship already exists"
            
            
            from app.models.module import Module        # Tikrinti ar moduliai egzistuoja
            module = Module.query.get(module_id)
            prerequisite = Module.query.get(prerequisite_id)
            
            if not module:
                return False, "Module not found"
            if not prerequisite:
                return False, "Prerequisite module not found"
            

            if module.study_program_id != prerequisite.study_program_id:     # Tikrinti ar tos pačios studijų programos
                return False, "Module and prerequisite must belong to the same study program"
            

            new_prereq = ModulePrerequisite(    # Sukurti naują prerequisite
                module_id=module_id,
                prerequisite_id=prerequisite_id
            )
            
            db.session.add(new_prereq)
            db.session.commit()
            return True, "Prerequisite created successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating prerequisite: {str(e)}"
        

    @staticmethod
    def remove_prerequisite(module_id, prerequisite_id):
        """Remove prerequisite relationship between modules"""
        try:
            prerequisite_record = ModulePrerequisite.query.filter_by( # rasti egzistuojanti prerequisite
                module_id=module_id,
                prerequisite_id=prerequisite_id
            ).first()
            
            if not prerequisite_record:
                return False, "Prerequisite relationship not found"
            
            db.session.delete(prerequisite_record)
            db.session.commit()
            return True, "Prerequisite removed successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error removing prerequisite: {str(e)}" 
        


    @staticmethod
    def get_module_prerequisites(module_id):
        """Get prerequisite modules for a specific module"""
        try:
            records = ModulePrerequisite.query.filter_by(module_id=module_id).all()
            return [record.prerequisite_module for record in records if record.prerequisite_module]
        except Exception as e:
            return []

    @staticmethod
    def get_modules_requiring(prerequisite_id):
        """Get all modules that require a specific prerequisite"""
        try:
            records = ModulePrerequisite.query.filter_by(prerequisite_id=prerequisite_id).all()
            return [record.module for record in records if record.module]
        except Exception as e:
            return []
        



    @staticmethod
    def check_student_can_enroll(student_id, module_id):
        """Check if a student can enroll in a module based on prerequisites"""
        try:
            from app.models.student_info import StudentInfo
            from app.models.module import Module
            
            student = StudentInfo.query.get(student_id)  # gaunam studentą ir modulį
            module = Module.query.get(module_id)
            
            if not student:
                return False, "Student not found"
            if not module:
                return False, "Module not found"
            
            # Gaunam prerequisite modulius
            required_modules = ModulePrerequisite.get_module_prerequisites(module_id)
            
            if not required_modules:
                return True, "there are no prerequisites for this module"
            
            # Gaunam studento užbaigtus modulius
            student_completed_ids = [
                enrollment.module_id 
                for enrollment in student.module_enrollments 
                if enrollment.status == 'completed' and 
                    enrollment.final_grade and 
                    enrollment.final_grade >= 5
            ]
            
            # Tikrinam ar visi prerequisite moduliai užbaigti
            missing_modules = []
            for required_module in required_modules:
                if required_module.id not in student_completed_ids:
                    missing_modules.append(required_module.name)
            
            if missing_modules:
                missing_names = ', '.join(missing_modules)
                return False, f"Missing prerequisite modules: {missing_names}"
            
            return True, "All prerequisites are met, student can enroll in the module"
            
        except Exception as e:
            return False, f"Prerequisite check error: {str(e)}"
    