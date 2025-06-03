# app/forms/test_forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from app.models import Assessment, Module

class TestForm(FlaskForm):
    """Testo kūrimo forma - tik atsiskaitymams"""
    
    title = StringField('Testo pavadinimas', validators=[DataRequired()])
    description = TextAreaField('Aprašymas (neprivaloma)')
    time_limit = IntegerField('Laiko limitas minutėmis (palikite tuščią jei nenorite)', 
                             validators=[Optional(), NumberRange(min=1)])
    max_attempts = IntegerField('Maksimalus bandymų skaičius', 
                               validators=[DataRequired(), NumberRange(min=1, max=3)], 
                               default=1)
    
    assessment_id = SelectField('Pasirinkite atsiskaitymą', 
                               coerce=int, 
                               validators=[DataRequired()])
    
    submit = SubmitField('Sukurti testą')

    def __init__(self, teacher_id=None, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        
        if teacher_id:
            assessments = Assessment.query.join(Module).outerjoin(
                Assessment.tests
            ).filter(
                Module.teacher_id == teacher_id,
                Assessment.is_active == True,
                Assessment.tests == None
            ).all()
            
            if assessments:
                self.assessment_id.choices = [
                    (a.id, f"{a.title} - {a.module.name}")
                    for a in assessments
                ]
            else:
                self.assessment_id.choices = []
        else:
            self.assessment_id.choices = []


class QuestionForm(FlaskForm):
    """Klausimo forma - tik multiple choice"""
    
    question = TextAreaField('Klausimas', validators=[DataRequired()])
    points = IntegerField('Kiek taškų už teisingą atsakymą', 
                         validators=[DataRequired(), NumberRange(min=1, max=5)], 
                         default=1)
    
    # 4 atsakymų variantai
    choice_a = StringField('A) Pirmas variantas', validators=[DataRequired()])
    choice_b = StringField('B) Antras variantas', validators=[DataRequired()])
    choice_c = StringField('C) Trečias variantas', validators=[DataRequired()])
    choice_d = StringField('D) Ketvirtas variantas', validators=[DataRequired()])
    
    # Teisingas atsakymas - tik vienas iš A, B, C, D
    correct_answer = SelectField('Teisingas atsakymas', 
                                choices=[
                                    ('A', 'A) Pirmas variantas'),
                                    ('B', 'B) Antras variantas'), 
                                    ('C', 'C) Trečias variantas'),
                                    ('D', 'D) Ketvirtas variantas')
                                ],
                                validators=[DataRequired()])
    
    submit = SubmitField('Pridėti klausimą')


class TestEditForm(FlaskForm):
    """Testo redagavimo forma"""
    
    title = StringField('Testo pavadinimas', validators=[DataRequired()])
    description = TextAreaField('Aprašymas')
    time_limit = IntegerField('Laiko limitas (minutės)', 
                             validators=[Optional(), NumberRange(min=1)])
    max_attempts = IntegerField('Maksimalus bandymų skaičius', 
                               validators=[DataRequired(), NumberRange(min=1, max=3)], 
                               default=1)
    
    submit = SubmitField('Išsaugoti pakeitimus')


class TestCompletionForm(FlaskForm):
    """Testo baigimo forma"""
    submit = SubmitField('Baigti testą')