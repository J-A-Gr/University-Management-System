from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models.module import Module
from app.extensions import db

bp = Blueprint('teacher', __name__)

@bp.route('/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        abort(403)

    teacher_info = current_user.teacher_info

    if not teacher_info:
        current_user.ensure_teacher_info()
        db.session.commit()
        teacher_info = current_user.teacher_info

    return render_template(
        'teacher/dashboard.html',
        teacher=current_user,
        schedule=teacher_info.get_schedule(),
        module_count=len(teacher_info.taught_modules)
    )

@bp.route('/schedule')
@login_required
def teacher_schedule():
    if not current_user.is_teacher:
        return "Unauthorized", 403

    return render_template(
        'teacher/teacher_schedule.html',
        schedule=current_user.teacher_info.get_schedule()
    )

@bp.route("/module/<int:module_id>/students")
@login_required
def view_module_students(module_id):
    if not current_user.is_teacher:
        return "Unauthorized", 403

    module = Module.query.get_or_404(module_id)

    # Apsauga – tik dėstytojas gali matyti savo modulį
    if module.teacher_id != current_user.teacher_info.id:
        return "Unauthorized", 403

    enrollments = module.enrollments  # ModuleEnrollment objektai
    return render_template("teacher/module_students.html", module=module, enrollments=enrollments)
