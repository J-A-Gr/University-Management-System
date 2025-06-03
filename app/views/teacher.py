from flask import Blueprint, render_template, abort, request, jsonify
from flask_login import login_required, current_user
from app.models import AttendanceRecord, Module, Assessment
from datetime import date
from app import db
from app.forms.attendance import AttendanceForm

bp = Blueprint('teacher', __name__)

@bp.route('/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        abort(403)

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

@bp.route("/module/<int:module_id>/students", methods=["GET", "POST"])
@login_required
def view_module_students(module_id):
    if not current_user.is_teacher:
        return "Unauthorized", 403

    form = AttendanceForm()
    module = Module.query.get_or_404(module_id)

    if module.teacher_id != current_user.teacher_info.id:
        return "Unauthorized", 403

    # Užpildom studentų pasirinkimus formoje
    form.student_id.choices = [
        (e.student_info.id, e.student_info.user.full_name)
        for e in module.enrollments
    ]

    if form.validate_on_submit():
        student_id = form.student_id.data
        attendance_date = form.date.data
        status = form.status.data

        existing = AttendanceRecord.query.filter_by(
            module_id=module_id,
            student_id=student_id,
            date=attendance_date
        ).first()

        if not existing:
            record = AttendanceRecord(
                student_id=student_id,
                module_id=module_id,
                date=attendance_date,
                status=status
            )
            db.session.add(record)
            db.session.commit()

        return render_template(
            "teacher/attendance_success.html",
            student_id=student_id,
            module=module,
            date=attendance_date,
            status=status
        )

    enrollments = module.enrollments
    return render_template(
        "teacher/module_students.html",
        module=module,
        enrollments=enrollments,
        form=form
    )
