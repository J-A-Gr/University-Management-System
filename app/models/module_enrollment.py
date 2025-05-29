from app.extensions import db
from datetime import datetime

class ModuleEnrollment(db.Model):
    """Studento registracija į modulį + lankomumas, pažymiai, statusas"""
    __tablename__ = 'module_enrollments'

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)

    semester = db.Column(db.Integer, nullable=False)
    final_grade = db.Column(db.Float, nullable=True)  # Galutinis pažymys
    attendance_percentage = db.Column(db.Float, default=0.0)
    completed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ryšiai
    student_info = db.relationship('StudentInfo', back_populates='module_enrollments')
    module = db.relationship('Module', back_populates='enrollments')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'module_id', name='unique_student_module'),
    )

    def __repr__(self):
        student_name = self.student_info.user.full_name if self.student_info and self.student_info.user else "Unknown"
        return f"<ModuleEnrollment {student_name} - {self.module.name}>"

    def mark_completed(self):
        """Pažymėti modulį kaip baigtą"""
        self.completed = True
        db.session.commit()

    def update_attendance(self, percentage):
        """Atnaujinti lankomumą"""
        try:
            if 0 <= percentage <= 100:
                self.attendance_percentage = percentage
                db.session.commit()
            else:
                raise ValueError("Attendance must be between 0 and 100")
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update attendance: {str(e)}")
