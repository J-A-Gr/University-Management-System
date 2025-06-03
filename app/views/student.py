from flask import Blueprint, render_template, redirect, url_for, session, request, abort, flash
from flask_login import login_required, current_user
from app.models import ModuleEnrollment, Module
from app.forms.student import EnrollModuleForm
from app.extensions import db
from collections import defaultdict

bp = Blueprint('student', __name__)


@bp.route('/select_module', methods=['POST'])
@login_required
def enroll_in_module():
    form = EnrollModuleForm()
    if form.validate_on_submit():
        module_id = int(form.module_id.data)
        module = Module.query.get_or_404(module_id)

        # Patikrinimai (jei reikia): ar modulis jau pasirinktas, ar atitinka semestrą, ir pan.

        enrollment = ModuleEnrollment(student_id=current_user.id, module_id=module.id)
        db.session.add(enrollment)
        db.session.commit()

        flash('Modulis sėkmingai pasirinktas.', 'success')
    else:
        flash('Registracija nepavyko.', 'danger')

    return redirect(url_for('modules.list_available_modules'))


@bp.route('/dashboard')
@login_required
def student_dashboard():
    try:
        if not current_user.is_student:
            abort(403)
        student_info = current_user.student_info
        schedule = student_info.get_schedule()
    except AttributeError:
        # Jei current_user neturi is_student atributo, tai reiškia, kad vartotojas nėra prisijungęs
        return redirect(url_for('auth.login'))

    return render_template(
        'student/dashboard.html',
        student=current_user,
        schedule=schedule,
        module_count=len(student_info.module_enrollments)
    )

@bp.route('/my_assessments')
@login_required
def my_assessments():
    """Studento atsiskaitymų peržiūra"""
    if not current_user.is_student:
        abort(403)
    
    if not current_user.student_info:
        flash('Studentas nerastas', 'error')
        return redirect(url_for('main.index'))
    
    try:
        # Gauti studento atsiskaitymus per modulių registracijas
        assessments = Assessment.query.join(Module).join(ModuleEnrollment).filter(
            ModuleEnrollment.student_info_id == current_user.student_info.id,
            ModuleEnrollment.status == 'active',
            Assessment.is_active == True
        ).order_by(Assessment.due_date.asc()).all()
        
        # Grupuoti pagal artimiausią datą
        from datetime import datetime
        now = datetime.now()
        
        upcoming = [a for a in assessments if a.due_date > now]
        past = [a for a in assessments if a.due_date <= now]
        
        return render_template('student/my_assessments.html', 
                             upcoming=upcoming, 
                             past=past,
                             total_count=len(assessments))
                             
    except Exception as e:
        flash(f'Klaida gaunant atsiskaitymus: {str(e)}', 'error')
        return redirect(url_for('student.student_dashboard'))

@bp.route('/schedule')
@login_required
def student_schedule():
    if not current_user.is_student:
        return "Unauthorized", 403

    student_info = current_user.student_info
    if not student_info:
        return render_template("student/student_schedule.html", schedule=None, error="Student profile not found")

    return render_template("student/student_schedule.html", schedule=student_info.get_schedule())




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