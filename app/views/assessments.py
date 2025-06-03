from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.forms.assessment import AssessmentForm, DeleteAssessmentForm
from app.models import Assessment, Module
from app.extensions import db

bp = Blueprint('assessments', __name__, url_prefix='/assessments')

@bp.route('/')
@login_required
def list_assessments():
    """Teacher's assessments overview"""
    if not current_user.is_teacher:
        abort(403)
    
    # Gauti savo modulių atsiskaitymus
    assessments = Assessment.query.join(Module).filter(
        Module.teacher_id == current_user.teacher_info.id
    ).order_by(Assessment.due_date.desc()).all()
    
    form = DeleteAssessmentForm()
    return render_template('assessments/list.html', assessments=assessments, form=form)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_assessment():
    """New assessment creation"""
    if not current_user.is_teacher:
        abort(403)
    
    form = AssessmentForm(teacher_id=current_user.teacher_info.id)
    
    if form.validate_on_submit():
        try:
            assessment = Assessment(
                title=form.title.data,
                description=form.description.data,
                due_date=form.due_date.data,
                assessment_type=form.assessment_type.data,
                max_points=form.max_points.data,
                module_id=form.module_id.data,
                created_by_teacher_id=current_user.teacher_info.id
            )
            
            db.session.add(assessment)
            db.session.commit()
            
            flash('Assessment created successfuly!', 'success')
            return redirect(url_for('assessments.list_assessments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating assessment: {str(e)}', 'error')
    return render_template('assessments/create.html', form=form)


@bp.route('/<int:assessment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_assessment(assessment_id):
    """Assessment editing"""
    if not current_user.is_teacher:
        abort(403)
    
    assessment = Assessment.query.get_or_404(assessment_id)
    
    # Patikrinam ar tai dėstytojo atsiskaitymas
    if assessment.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    form = AssessmentForm(teacher_id=current_user.teacher_info.id, obj=assessment)
    
    if form.validate_on_submit():
        try:
            assessment.title = form.title.data
            assessment.description = form.description.data
            assessment.due_date = form.due_date.data
            assessment.assessment_type = form.assessment_type.data
            assessment.max_points = form.max_points.data
            assessment.module_id = form.module_id.data
            
            db.session.commit()
   
            flash('Assessment updated!', 'success')
            return redirect(url_for('assessments.list_assessments'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating assessment: {str(e)}', 'error')

    return render_template('assessments/edit.html', form=form, assessment=assessment)


@bp.route('/<int:assessment_id>/toggle', methods=['POST'])
@login_required
def toggle_assessment(assessment_id):
    """Assessment activation/deactivation"""
    if not current_user.is_teacher:
        abort(403)
    
    assessment = Assessment.query.get_or_404(assessment_id)
    
    if assessment.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    form = DeleteAssessmentForm()
    if form.validate_on_submit():
        try:
            assessment.is_active = not assessment.is_active
            db.session.commit()
            
            status = "active" if assessment.is_active else "canceled"
            flash(f'Assessment {status}!', 'info')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error changing status: {str(e)}', 'error')
    
    return redirect(url_for('assessments.list_assessments'))