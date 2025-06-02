from flask import Blueprint, render_template, redirect, url_for, session, abort, flash
from flask_login import login_required, current_user
from app.models import ModuleEnrollment
from collections import defaultdict

bp = Blueprint('student', __name__)

@bp.route('/dashboard')
@login_required
def student_dashboard():
    if not current_user.role == 'student':
        abort(403)

    return render_template('student/dashboard.html', student=current_user) # student=student_info, modules=modules, gpa=gpa)

@bp.route('/schedule')
@login_required
def student_schedule():
    if not current_user.is_student:
        return "Unauthorized", 403

    student_info = current_user.student_info
    if not student_info:
        return render_template("student/student_schedule.html", schedule=None, error="Student profile not found")
    enrollments = student_info.module_enrollments  # pasitraukiam visus modelius, kuriuos turi studentas

    schedule = defaultdict(list) # Tvarkaraščio struktūros paruošimas

    for enrollment in enrollments: # Iteruojame per kiekvieną modulį, kur studentas yra užsiregistravęs.
        module = enrollment.module
        teacher_name = (
            f"{module.teacher.user.first_name} {module.teacher.user.last_name}"
            if module.teacher and module.teacher.user else "Nenurodyta"
        )
        # Aktyvių atsiskaitymų paėmimas
        assessments_data = [
            {
                "title": a.title,
                "type": a.assessment_type,
                "due_date": a.due_date.strftime("%Y-%m-%d")
            }
            for a in module.assessments if a.is_active
        ]

        schedule[module.day_of_week].append({
            "module_name": module.name,
            "start_time": module.start_time.strftime("%H:%M"),
            "end_time": module.end_time.strftime("%H:%M"),
            "room": module.room,
            "teacher": teacher_name,
            "assessments": assessments_data
        })

    return render_template('student/student_schedule.html', schedule=dict(schedule))



@bp.route('/modules')
@login_required
def student_module():
    if not current_user.is_student:
        return "Unauthorized", 403

    student_info = current_user.student_info
    if not student_info:
        return render_template("student/student_schedule.html", schedule=None, error="Student profile not found")
    enrollments = student_info.module_enrollments  # pasitraukiam visus modelius, kuriuos turi studentas

    schedule = defaultdict(list) # Tvarkaraščio struktūros paruošimas

    for enrollment in enrollments: # Iteruojame per kiekvieną modulį, kur studentas yra užsiregistravęs.
        module = enrollment.module
        teacher_name = (
            f"{module.teacher.user.first_name} {module.teacher.user.last_name}"
            if module.teacher and module.teacher.user else "Nenurodyta"
        )
        # Aktyvių atsiskaitymų paėmimas
        assessments_data = [
            {
                "title": a.title,
                "type": a.assessment_type,
                "due_date": a.due_date.strftime("%Y-%m-%d")
            }
            for a in module.assessments if a.is_active
        ]

        schedule[module.day_of_week].append({
            "module_name": module.name,
            "start_time": module.start_time.strftime("%H:%M"),
            "end_time": module.end_time.strftime("%H:%M"),
            "room": module.room,
            "teacher": teacher_name,
            "assessments": assessments_data
        })

    return render_template('student/modules.html', schedule=dict(schedule)) # TODO reik sukurti student/modules.html