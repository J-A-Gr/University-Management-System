from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.module import ModuleForm  
from app.models import Module, StudyProgram, TeacherInfo
from app.extensions import db

bp = Blueprint('modules', __name__, url_prefix='/modules')


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_module():
    form = ModuleForm()

    # Užkraunam pasirinkimų sąrašus atskirai
    study_programs = StudyProgram.query.all()
    teachers = TeacherInfo.query.all()
    active_modules = Module.query.filter_by(is_active=True).all() # Šitie duomenys bus naudojami formos dropdown pasirinkimuose

    # Paskiriame pasirinkimus formai
    form.study_program_id.choices = [(program.id, program.name) for program in study_programs]

    form.teacher_id.choices = [(0, '-- Pasirinkti --')] + [
        (teacher.id, teacher.user.full_name) for teacher in teachers
    ]
    # TODO naudotojas gali pasirinkti kelis modulius laikant Ctrl (arba naudojant checkbox’us JS’e, jei norėsi pagražinti vėliau)
    # (SelectMultipleField flask formos momentas.)
    form.prerequisite_module_ids.choices = [(module.id, module.name) for module in active_modules] # 


    if form.validate_on_submit():
        try:
            module = Module(
                name=form.name.data,
                description=form.description.data,
                credits=form.credits.data,
                semester=form.semester.data,
                day_of_week=form.day_of_week.data, 
                start_time=form.start_time.data, 
                end_time=form.end_time.data,
                room=form.room.data,
                study_program_id=form.study_program_id.data,
                created_by_id=current_user.id,
                teacher_id=form.teacher_id.data if form.teacher_id.data != 0 else None
            )

            db.session.add(module)
            db.session.commit()

            flash('Modulis sėkmingai sukurtas!', 'success')
            return redirect(url_for('modules.create_module'))

        except Exception as e:
            db.session.rollback()
            flash(f"Klaida kuriant modulį: {str(e)}", 'danger')
    return render_template('modules/create_module.html', form=form)
