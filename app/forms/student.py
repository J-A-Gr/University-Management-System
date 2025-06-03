from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms.validators import DataRequired

class EnrollModuleForm(FlaskForm):
    module_id = HiddenField(validators=[DataRequired()])