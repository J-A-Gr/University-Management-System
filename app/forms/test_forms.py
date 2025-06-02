from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from app.models import Module, Assessment

class TestForm(FlaskForm):
    title = StringField('Test title', validators=[
        DataRequired(message='Test title is required'), 
        Length(min=3, max=200, message='Test title must be 3-200 characters long'   )
    ])
    description = TextAreaField('Description', validators=[Optional()])
    time_limit = IntegerField('Time limit (minutes)', validators=[
        Optional(), 
        NumberRange(min=1, max=300, message='Time limit must be between 1 and 300 minutes')
    ])
    max_attempts = IntegerField('Maximum number of attempts', validators=[
        DataRequired(message='Attempt count is mandatory'), 
        NumberRange(min=1, max=10, message='Number of attempts must be 1-10')
    ], default=1)
    show_results_immediately = BooleanField('Display results instantly', default=True)
    stop_after_pass = BooleanField('Stop after positive assessment', default=True)
    
    module_id = SelectField('Module', 
                            validators=[DataRequired(message='Module is required')],
                            coerce=int)
        
    assessment_id = SelectField('Exam (optional)', 
                               coerce=int,
                               validate_choice=False) 


    submit = SubmitField('Create test')


    def __init__(self, teacher_id=None, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        
        if teacher_id:
                # Užpildyti modulių pasirinkimus
            modules = Module.query.filter_by(teacher_id=teacher_id, is_active=True).all()
            self.module_id.choices = [(m.id, m.name) for m in modules]
                
                # Užpildyti egzaminų pasirinkimus
            module_ids = [m.id for m in modules]
            assessments = Assessment.query.filter(
                Assessment.module_id.in_(module_ids),
                Assessment.assessment_type == 'egzaminas',
                Assessment.is_active == True
            ).all()
                
                # Pridėti egzaminus prie choices
            assessment_choices = [('', 'Select exam...')]
            assessment_choices.extend([(a.id, a.title) for a in assessments])
            self.assessment_id.choices = assessment_choices
        
        else:
                # Default choices - JEI NĖRA teacher_id
            self.module_id.choices = []
            self.assessment_id.choices = [('', 'Select exam...')]


class TestQuestionForm(FlaskForm):
    question = TextAreaField('Question', validators=[
        DataRequired(message='Question text is required'), 
        Length(min=5, max=1000, message='Question must be between 5 and 1000 characters')
    ])
    question_type = SelectField('Question type', 
                               choices=[('open', 'Open question')],
                               validators=[DataRequired()],
                               default='open')
    points = IntegerField('Points', validators=[
        DataRequired(message='Points count is required'), 
        NumberRange(min=1, max=10, message='Points count must be 1-10')
    ], default=1)
    correct_answer = StringField('Correct answer', validators=[
        DataRequired(message='Correct answer is required for open questions'),
        Length(min=1, max=500, message='Answer must be 1-500 characters')
    ])
    submit = SubmitField('Add question')


class EditTestQuestionForm(FlaskForm):
    question_id = HiddenField()
    question = TextAreaField('Question', validators=[DataRequired(), Length(min=5, max=1000)])
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=1, max=10)])
    correct_answer = StringField('Correct answer', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Update question')

class StudentAnswerForm(FlaskForm):
    """Form for student to submit answers"""
    pass  # Dinamiškai sukuriama view'e

class TestCompletionForm(FlaskForm):
    """Form for completing test"""
    submit = SubmitField('Complete test')