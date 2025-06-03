from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, SubmitField
from wtforms.validators import DataRequired

class AttendanceForm(FlaskForm):
    student_id = SelectField("Studentas", coerce=int, validators=[DataRequired()])
    date = DateField("Data", validators=[DataRequired()])
    status = SelectField("Statusas", choices=[
        ('atvyko', 'Atvyko'),
        ('pavėlavo', 'Pavėlavo'),
        ('neatvyko', 'Neatvyko'),
        ('pateisinta', 'Pateisinta')
    ], validators=[DataRequired()])
    submit = SubmitField("Žymėti")