from app.extensions import db
from datetime import date

class AttendanceRecord(db.Model):
    """Modelis studentų lankomumui žymėti"""
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)  # Unikalus identifikatorius

    # Kuris modulis (paskaita) buvo lankyta
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)

    # Kuris studentas
    student_id = db.Column(db.Integer, db.ForeignKey('student_info.id'), nullable=False)

    # Lankomumo data
    date = db.Column(db.Date, default=date.today, nullable=False)

    # Lankomumo būsena – galimos reikšmės: atvyko, pavėlavo, neatvyko, pateisinta
    status = db.Column(
        db.Enum('atvyko', 'pavėlavo', 'neatvyko', 'pateisinta', name='attendance_status'),
        default='atvyko',
        nullable=False
    )

    # Santykiai su kitais modeliais
    module = db.relationship('Module', back_populates='attendance_records')
    student = db.relationship('StudentInfo', back_populates='attendance_records')

    # Užtikriname, kad studentas negali būti pažymėtas daugiau nei vieną kartą tą pačią dieną tame pačiame modulyje
    __table_args__ = (
        db.UniqueConstraint('module_id', 'student_id', 'date', name='unique_attendance_per_day'),
    )

    def __repr__(self):
        return f"<AttendanceRecord {self.date} - Student {self.student_id} in Module {self.module_id}: {self.status}>"
