from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from app.forms.main import ProfileForm
from app.extensions import db
from app.utils.decorators import admin_required

bp = Blueprint('main', __name__)


@bp.route('/')
@bp.route('/index')
def index():
    """Home page"""
    return render_template('index.html', title='Home')


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('profile.html', title='Profile', form=form)


@bp.route('/dashboard', endpoint='dashboard')
@login_required
def universal_dashboard():
    match current_user.role:
        case 'student':
            return redirect(url_for('student.student_dashboard'))
        case 'teacher':
            return redirect(url_for('teacher.teacher_dashboard'))
        case 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        case _:
            abort(403)


@bp.route('/select-subjects')
@login_required
def select_subjects():
    """Select subjects page"""
    # Nukreipti pagal vartotojo tipą
    if current_user.is_student:
        return redirect(url_for('student_tests.available_tests'))
    elif current_user.is_teacher:
        return redirect(url_for('teacher_tests.my_tests'))
    else:
        return redirect(url_for('main.dashboard'))