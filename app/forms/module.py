from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, TimeField, SelectMultipleField
from wtforms.validators import DataRequired, NumberRange

class ModuleForm(FlaskForm):
    name = StringField('Pavadinimas', validators=[DataRequired()])
    description = TextAreaField('Aprašymas', validators=[DataRequired()])
    credits = IntegerField('Kreditai', validators=[DataRequired(), NumberRange(min=1)])

    semester = SelectField('Semestras', choices=[('rudens', 'Rudens'), ('pavasario', 'Pavasario')], validators=[DataRequired()])
    day_of_week = SelectField('Paskaitos diena', choices=[
        ('pirmadienis', 'Pirmadienis'),
        ('antradienis', 'Antradienis'),
        ('trečiadienis', 'Trečiadienis'),
        ('ketvirtadienis', 'Ketvirtadienis'),
        ('penktadienis', 'Penktadienis')
    ], validators=[DataRequired()])

    start_time = TimeField('Pradžia', validators=[DataRequired()])
    end_time = TimeField('Pabaiga', validators=[DataRequired()])
    room = StringField('Auditorija')

    study_program_id = SelectField('Studijų programa', coerce=int, validators=[DataRequired()])
    teacher_id = SelectField('Dėstytojas', coerce=int, choices=[], validate_choice=False)  # gali būti tuščias

    prerequisite_module_ids = SelectMultipleField('Priklausomi moduliai', coerce=int, validate_choice=False)
