from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from collections import defaultdict
from app.models.module import Module

bp = Blueprint('teacher', __name__)

@bp.route('/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        abort(403)
    return render_template('teacher/dashboard.html', teacher=current_user)

@bp.route('/schedule')
@login_required
def teacher_schedule():
    if not current_user.is_teacher:
        return "Unauthorized", 403

    teacher_info = current_user.teacher_info
    modules = teacher_info.taught_modules

    schedule = defaultdict(list)

    for module in modules:
        assessments_data = [
            {
                "title": a.title,
                "type": a.assessment_type,
                "due_date": a.due_date.strftime("%Y-%m-%d")
            }
            for a in module.assessments if a.is_active
        ]

        schedule[module.day_of_week].append({
            "module_id": module.id,
            "module_name": module.name,
            "start_time": module.start_time.strftime("%H:%M"),
            "end_time": module.end_time.strftime("%H:%M"),
            "room": module.room,
            "assessments": assessments_data
        })

    return render_template('teacher/teacher_schedule.html', schedule=dict(schedule))

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
