from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import datetime
from app.models import Module


class AssessmentForm(FlaskForm):
    """Assessment form for creating or editing assessments"""
    
    title = StringField('Pavadinimas', validators=[DataRequired()])
    description = TextAreaField('Aprašymas', validators=[DataRequired()])
    due_date = DateTimeField('Data ir laikas', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    assessment_type = SelectField('Tipas', choices=[
        ('egzaminas', 'Egzaminas'),
        ('uzduotis', 'Užduotis'),
        ('testas', 'Testas'),
        ('laboratorinis', 'Laboratorinis')
    ], validators=[DataRequired()])
    max_points = IntegerField('Maksimalūs balai', validators=[DataRequired(), NumberRange(min=1, max=100)], default=10)
    module_id = SelectField('Modulis', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Sukurti')
    
    def __init__(self, teacher_id=None, *args, **kwargs):
        super(AssessmentForm, self).__init__(*args, **kwargs)
        
        if teacher_id:
            modules = Module.query.filter_by(teacher_id=teacher_id, is_active=True).all()
            self.module_id.choices = [(m.id, m.name) for m in modules]
        else:
            self.module_id.choices = []
    
    def validate_due_date(self, field):
        if field.data and field.data <= datetime.now():
            raise ValidationError('Date and time must be in the future')


class DeleteAssessmentForm(FlaskForm):
    """CSRF form for deleting assessments"""
    pass