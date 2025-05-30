from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.module import ModuleForm, DeleteForm
from app.models import Module, StudyProgram, TeacherInfo, ModulePrerequisite, User, ModuleEnrollment
from app.extensions import db

bp = Blueprint('modules', __name__, url_prefix='/modules')


@bp.route('/')
@login_required
def list_modules():
    form = DeleteForm() # CSRF hiddeng_tag()
    modules = Module.query.order_by(Module.name).all()
    return render_template('modules/list_modules.html', modules=modules, form=form)

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
                teacher_id=form.teacher_id.data if form.teacher_id.data != 0 else None,
                is_active=True  # <-- pažymim kaip aktyvų
            )
            db.session.add(module)
            db.session.commit()

            # Pridėti priklausomus modulius (BONUS POINTS)
            for prereq_id in form.prerequisite_module_ids.data:
                prereq = ModulePrerequisite(module_id=module.id, prerequisite_id=prereq_id)
                db.session.add(prereq)

            db.session.commit()

            flash('Modulis sėkmingai sukurtas!', 'success')
            return redirect(url_for('modules.view_module', module_id=module.id))  # <-- geresnis redirect‘as

        except Exception as e:
            db.session.rollback()
            flash(f"Klaida kuriant modulį: {str(e)}", 'danger')

    return render_template('modules/create_module.html', form=form)



@bp.route('/<int:module_id>')
@login_required
def view_module(module_id):
    module = Module.query.get_or_404(module_id)

    prerequisites = ModulePrerequisite.query\
        .filter_by(module_id=module.id)\
        .join(Module, Module.id == ModulePrerequisite.prerequisite_id)\
        .all()

    enrolled_students = User.query\
        .join(ModuleEnrollment, ModuleEnrollment.student_info_id == User.id)\
        .filter(ModuleEnrollment.module_id == module.id)\
        .all()

    form = DeleteForm()
    return render_template('modules/view_module.html', module=module,
                           prerequisites=prerequisites,
                           enrolled_students=enrolled_students,
                           form=form)  # būtina, nes šablonas naudoja form.hidden_tag()



@bp.route('/<int:module_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_module(module_id):
    module = Module.query.get_or_404(module_id)
    form = ModuleForm(obj=module)

    # Pasirinkimų sąrašai
    study_programs = StudyProgram.query.all()
    teachers = TeacherInfo.query.all()
    active_modules = Module.query.filter(Module.id != module.id, Module.is_active == True).all()

    form.study_program_id.choices = [(sp.id, sp.name) for sp in study_programs]
    form.teacher_id.choices = [(0, '-- Pasirinkti --')] + [
        (t.id, t.user.full_name) for t in teachers
    ]
    form.prerequisite_module_ids.choices = [(m.id, m.name) for m in active_modules]

    # Užpildom checkboxus (tik GET metu)
    if request.method == "GET":
        form.prerequisite_module_ids.data = [
            prereq.prerequisite_id for prereq in module.prerequisite_records
        ]

    if form.validate_on_submit():
        try:
            module.name = form.name.data
            module.description = form.description.data
            module.credits = form.credits.data
            module.semester = form.semester.data
            module.day_of_week = form.day_of_week.data
            module.start_time = form.start_time.data
            module.end_time = form.end_time.data
            module.room = form.room.data
            module.study_program_id = form.study_program_id.data
            module.teacher_id = form.teacher_id.data if form.teacher_id.data != 0 else None

            # Ištrinam senus prerequisites
            ModulePrerequisite.query.filter_by(module_id=module.id).delete()

            # Pridedam naujus prerequisites
            for prereq_id in form.prerequisite_module_ids.data:
                new_prereq = ModulePrerequisite(
                    module_id=module.id,
                    prerequisite_id=prereq_id
                )
                db.session.add(new_prereq)

            db.session.commit()
            flash("Modulio duomenys atnaujinti", "success")
            return redirect(url_for("modules.view_module", module_id=module.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Klaida atnaujinant modulį: {str(e)}", "danger")

    return render_template("modules/edit_module.html", form=form, module=module)


@bp.route('/<int:module_id>/delete', methods=['POST'])
@login_required
def delete_module(module_id):
    form = DeleteForm()
    if not form.validate_on_submit():
        flash("Neteisinga forma (gal CSRF tokenas negalioja?)", "danger")
        return redirect(url_for('modules.view_module', module_id=module_id))

    module = Module.query.get_or_404(module_id)

    try:
        # Prieš trynimą – pašalinti visus priklausomus įrašus
        ModulePrerequisite.query.filter(
            (ModulePrerequisite.module_id == module.id) | 
            (ModulePrerequisite.prerequisite_id == module.id)
        ).delete(synchronize_session=False)

        # Pašalinti visus įvertinimus
        from app.models import Assessment  # Jei dar neturi importuota viršuje
        Assessment.query.filter_by(module_id=module.id).delete(synchronize_session=False)

        # Pašalinti studentų registracijas
        ModuleEnrollment.query.filter_by(module_id=module.id).delete(synchronize_session=False)

        # Galiausiai pašalinti modulį
        db.session.delete(module)
        db.session.commit()

        flash("Modulis sėkmingai ištrintas.", "info")
        return redirect(url_for('modules.list_modules'))

    except Exception as e:
        db.session.rollback()
        flash(f"Klaida šalinant modulį: {str(e)}", "danger")
        return redirect(url_for('modules.view_module', module_id=module.id))
