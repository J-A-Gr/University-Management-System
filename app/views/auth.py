from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms.auth import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from app.models import User, StudyProgram, Group
from app.extensions import db, bcrypt
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import os
import uuid
from app.config import Config
from app.utils.helpers import allowed_file
from app.services.group_services import find_or_create_available_group


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user:
            # Patikrinam ar vartotojas yra užrakintas
            if user.is_locked():
                flash('Account is locked due to too many failed login attempts. Try again later.', 'error')
                return redirect(url_for('auth.login'))

            # Tikrinam slaptažodį
            if user.check_password(form.password.data):
                if not user.is_active:
                    flash('Account is deactivated. Contact support.', 'error')
                    return redirect(url_for('auth.login'))

                # Login sėkmingas – resetinam skaitiklį
                user.failed_login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.utcnow()
                db.session.commit()

                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.first_name}!', 'success')
                return redirect(next_page or url_for('main.dashboard'))
            else:
                # užtikrinam, kad skaitiklis niekad nėra None, kitaip gausim TypeError...
                if user.failed_login_attempts is None:
                    user.failed_login_attempts = 0
                # Netinkamas slaptažodis – didinam skaitiklį
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 3:
                    user.locked_until = datetime.utcnow() + timedelta(minutes=5)
                    flash('Account locked due to 3 failed login attempts. Try again in 5 minutes.', 'error')
                else:
                    flash('Invalid email or password', 'error')
                db.session.commit()
                return redirect(url_for('auth.login'))
        
        # Jei user neegzistuoja
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    form.study_program.choices = [(p.id, p.name) for p in StudyProgram.query.all()]
    
    if form.validate_on_submit():

        profile_filename = 'default.png'  # apsauga nuo sulūžimo (jeigu neįkeltų failo(image))
        file = form.profile_picture.data

        if file and allowed_file(file.filename):  # tikrinam ar įkeltas failas (none ar ne) ir jo formatą 
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"  # uuid sugeneruoja unikalų string (apsauga nuo pasikartojančio pav.)
            file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            profile_filename = unique_filename 

        role = form.role.data
        user = User(
            is_student=(role == 'student'),
            is_teacher=(role == 'teacher'),
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birthday=form.birthday.data,
            profile_picture=profile_filename  # į db keliauja pavadinimas nuotraukos
        )
        user.set_password(form.password.data)

        if user.is_student:  # programos kodo sugeneravimas
            current_year = datetime.utcnow().year  # dabartiniai metai
            group = find_or_create_available_group(form.study_program.data, current_year)

            user.ensure_student_info()  # įsitikinam, kad jis turi StudentInfo
            user.student_info.study_program_id = form.study_program.data  # Priskiriam studijų programa
            user.student_info.admission_year = current_year  # automatiškai priskiria įstojimo metus
            user.student_info.group = group  # priskiriam grupę

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            # In a real app, send reset email here
            flash('Check your email for password reset instructions.', 'info')
        else:
            flash('Email address not found.', 'error')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.login'))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_reset_token()
        flash('Your password has been reset successfully.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Reset Password', form=form)


@bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify email address"""
    user = User.query.filter_by(email_verification_token=token).first()
    if user and user.verify_email_token(token):
        flash('Email verified successfully!', 'success')
    else:
        flash('Invalid verification token.', 'error')
    return redirect(url_for('auth.login'))


@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
