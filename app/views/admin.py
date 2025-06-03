from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import current_user
from app.extensions import db
from app.utils.decorators import admin_required
from app.models import User, Module, StudyProgram, Group
from sqlalchemy import func
from app.forms.admin import EmptyForm
from collections import defaultdict

bp = Blueprint('admin', __name__)


@bp.route('/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.role == 'admin':
        abort(403)

    form = EmptyForm()
    search = request.args.get('search', '').strip()  # paieškos laukui naudojama, (Kai forma siunčiama su GET)

    query = User.query

    # papildomas filtravimas
    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.filter( db.func.lower(User.email).like(search_pattern)) # WHERE LOWER(email) LIKE '%email@...@%'

    # Adminai viršuje, paprasti useriai sekantys.
    users = query.order_by(User.is_admin.desc(), User.email.asc()).all()

    # statistinė informacija
     
    try:
        user_count = User.query.count()
        module_count = Module.query.count()
        program_count = StudyProgram.query.count()
        group_count = Group.query.count()
    except Exception as e:
        flash(f"Error counting statistics: {str(e)}", "error")
        user_count = module_count = program_count = group_count = 0


    return render_template('admin/dashboard.html', 
                            title='Admin Panel', 
                            users=users, 
                            search=search, 
                            form=form,
                            user_count=user_count,
                            module_count=module_count,
                            program_count=program_count,
                            group_count=group_count)


@bp.route('/promote/<int:user_id>', methods=['POST'])
@admin_required
def promote_user(user_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)

        if user.is_admin:
            flash(f"User '{user.email}' is already an admin.", "error")
        else:
            user.is_admin = True
            db.session.commit()
            flash(f"User '{user.email}' has been promoted to admin.", "success")

    return redirect(url_for('admin.admin_dashboard'))

@bp.route('/demote/<int:user_id>', methods=['POST'])
@admin_required
def demote_user(user_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)

        # Apsauga nuo hardcodinto admino pašalinimo.
        if user.email == "admin@example.com":
            flash("Cannot demote the 'super' admin.", "error") 
            return redirect(url_for('admin.admin_dashboard'))
        
        if not user.is_admin:
            flash(f"User '{user.email}' is not an admin.", "error")
        else:
            user.is_admin = False
            db.session.commit()
            flash(f"User '{user.email}' has been demoted from admin.", "success")

    return redirect(url_for('admin.admin_dashboard'))


@bp.route('/schedule/<int:user_id>')
@admin_required
def admin_schedule(user_id):
    if not current_user.is_admin:
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    schedule = defaultdict(list)

    if user.is_student:
        enrollments = user.student_info.module_enrollments
        for enrollment in enrollments:
            module = enrollment.module
            teacher = module.teacher.user.full_name if module.teacher else "Nenurodyta"
            assessments = [
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
                "teacher": teacher,
                "assessments": assessments
            })

    elif user.is_teacher:
        modules = user.teacher_info.taught_modules
        for module in modules:
            assessments = [
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
                "assessments": assessments
            })

    else:
        return render_template("admin/admin_schedule.html", user=user, schedule=None, is_unknown=True)

    return render_template("admin/admin_schedule.html", user=user, schedule=dict(schedule), is_unknown=False)

'''Palieku dėl visa ko, bet nereikalingas kaip ir manage_users.html, edit_user.html (pasikeitė logika...)'''
# @bp.route('/users')
# @admin_required
# def manage_users():
#     """Admin: Manage users"""
#     form = EmptyForm()
#     users = User.query.order_by(User.email.asc()).all()
#     programs = StudyProgram.query.order_by(StudyProgram.name.asc()).all()
#     return render_template('admin/manage_users.html', users=users, programs=programs, form=form)

# @bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
# @admin_required
# def edit_user(user_id):
#     user = User.query.get_or_404(user_id)
#     programs = StudyProgram.query.all()
#     form = EmptyForm()

#     if request.method == 'POST' and form.validate_on_submit():
#         try:
#             new_role = request.form.get('role')

#             # Jei ne admin@example.com – leidžiam keisti rolę
#             if not user.is_admin and new_role in ['student', 'teacher']:
#                 user.set_role(new_role)

#             # Užtikrinam, kad atitinkami info objektai egzistuoja
#             user.ensure_student_info()
#             user.ensure_teacher_info()

#             # Atnaujinam aktyvumą
#             user.is_active = 'is_active' in request.form

#             # Jei studentas – atnaujinam studijų programą
#             if user.is_student and user.student_info:
#                 new_program_id = request.form.get('program_id')
#                 if new_program_id:
#                     user.change_study_program(new_program_id)

#             db.session.commit()
#             flash("User updated successfully", "success")
#             return redirect(url_for('admin.manage_users'))

#         except Exception as e:
#             db.session.rollback()
#             flash(f"Error while updating user: {e}", "error")

#     return render_template('admin/edit_user.html', user=user, programs=programs, form=form)


# @bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
# @admin_required
# def deactivate_user(user_id):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         user = User.query.get_or_404(user_id)
#         if user.email == "admin@example.com":
#             flash("Can't deactivate super admin", "danger")
#             return redirect(url_for('admin.manage_users'))
#         user.is_active = False
#         db.session.commit()
#         flash("User deactivated", "info")
#     return redirect(url_for('admin.manage_users'))

# @bp.route('/users/<int:user_id>/delete', methods=['POST'])
# @admin_required
# def delete_user(user_id):
#     form = EmptyForm()
#     if form.validate_on_submit():
#         user = User.query.get_or_404(user_id)
#         if user.email == "admin@example.com":
#             flash("Can't delete super admin.", "danger")
#             return redirect(url_for('admin.manage_users'))
#         db.session.delete(user)
#         db.session.commit()
#         flash("User deleted", "warning")
#     return redirect(url_for('admin.manage_users'))