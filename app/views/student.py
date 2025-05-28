from flask import Blueprint, render_template, redirect, url_for, session, abort, flash
from flask_login import login_required, current_user

bp = Blueprint('student', __name__)

@bp.route('/dashboard')
@login_required
def student_dashboard():
    if not current_user.role == 'student':
        abort(403)

    """visas šitas malonumas bus apjungtas po modelių užbaigtumo."""

    # student_info = current_user.student_info
    # if not student_info:
    #     flash("Student profile is incomplete.", "error")
    #     abort(403)

    # modules = student_info.get_enrolled_modules()
    # gpa = student_info.calculate_gpa()

    return render_template('student/dashboard.html', student=current_user) # student=student_info, modules=modules, gpa=gpa)

