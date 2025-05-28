from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

bp = Blueprint('teacher', __name__)

@bp.route('/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        abort(403)
    return render_template('teacher/dashboard.html', teacher=current_user)


"""FOR THE NEAR FUTURE"""
# @bp.route('/modules')
# @login_required
# def modules():
#     if current_user.role != 'teacher':
#         abort(403)
    
#     teacher_modules = current_user.teacher_info.modules  # assumes relationship
#     return render_template('teacher/modules.html', modules=teacher_modules)


# @bp.route('/module/create', methods=['GET', 'POST'])
# @login_required
# def create_module():
#     ...


# @bp.route('/module/<int:id>/edit', methods=['GET', 'POST'])
# @login_required
# def edit_module(id):
#     ...
