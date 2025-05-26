from flask_wtf import FlaskForm
'''Sukurta, kad Flask-WTF galėtų patikrinti CSRF token, leidžia naudoti
į html formą įsidėti {{ form.csrf_token }}, kuris susijęs su FlaskForm'''
class EmptyForm(FlaskForm):
    pass

