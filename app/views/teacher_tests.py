from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from app.models import Test, TestQuestion, Module, Assessment, TestResult
from app.forms.test_forms import TestForm, TestQuestionForm, EditTestQuestionForm
from app.extensions import db

bp = Blueprint('teacher_tests', __name__, url_prefix='/teacher/tests')

@bp.route('/')
@login_required
def my_tests():
    """Teacher's tests overview"""
    if not current_user.is_teacher:
        abort(403)
    
    tests = Test.query.filter_by(
        created_by_teacher_id=current_user.teacher_info.id
    ).order_by(Test.created_at.desc()).all()
    
    return render_template('teacher/tests/my_tests.html', tests=tests)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_test():
    """New test creation"""
    if not current_user.is_teacher:
        abort(403)
    
    form = TestForm(teacher_id=current_user.teacher_info.id)
    
    if form.validate_on_submit():
        module = Module.query.get(form.module_id.data)
        if not module or module.teacher_id != current_user.teacher_info.id:
            abort(403)
        
        assessment_id = None
        if form.assessment_id.data and form.assessment_id.data != '':
            assessment_id = form.assessment_id.data
        
        test = Test(
            title=form.title.data,
            description=form.description.data,
            time_limit=form.time_limit.data,
            max_attempts=form.max_attempts.data,
            show_results_immediately=form.show_results_immediately.data,
            stop_after_pass=form.stop_after_pass.data,
            module_id=form.module_id.data,  
            assessment_id=assessment_id,    
            created_by_teacher_id=current_user.teacher_info.id
        )
        
        db.session.add(test)
        db.session.commit()
        
        return redirect(url_for('teacher_tests.edit_test', test_id=test.id))
    
    return render_template('teacher/tests/create_test.html', form=form)

@bp.route('/<int:test_id>/edit')
@login_required
def edit_test(test_id):
    """Test editing page"""
    if not current_user.is_teacher:
        abort(403)
    
    test = Test.query.get_or_404(test_id)
    
    if test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    questions = TestQuestion.get_questions_by_position(test_id)
    question_form = TestQuestionForm()
    edit_form = EditTestQuestionForm()
    
    return render_template('teacher/tests/edit_test.html', 
                         test=test, 
                         questions=questions, 
                         question_form=question_form,
                         edit_form=edit_form)

@bp.route('/<int:test_id>/add_question', methods=['POST'])
@login_required
def add_question(test_id):
    """Question addition to a test"""
    if not current_user.is_teacher:
        abort(403)
    
    test = Test.query.get_or_404(test_id)
    
    if test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    form = TestQuestionForm()
    
    if form.validate_on_submit():
        question = TestQuestion(
            question=form.question.data,
            question_type=form.question_type.data,
            points=form.points.data,
            correct_answer=form.correct_answer.data,
            test_id=test_id,
            position=TestQuestion.get_next_position(test_id)
        )
        
        db.session.add(question)
        db.session.commit()
    
    return redirect(url_for('teacher_tests.edit_test', test_id=test_id))

@bp.route('/question/<int:question_id>/edit', methods=['POST'])
@login_required
def edit_question(question_id):
    """Question editing"""
    if not current_user.is_teacher:
        abort(403)
    
    question = TestQuestion.query.get_or_404(question_id)
    
    if question.test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    form = EditTestQuestionForm()
    
    if form.validate_on_submit():
        question.question = form.question.data
        question.points = form.points.data
        question.correct_answer = form.correct_answer.data
        
        db.session.commit()
    
    return redirect(url_for('teacher_tests.edit_test', test_id=question.test_id))

@bp.route('/question/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    """Delete question from a test"""
    if not current_user.is_teacher:
        abort(403)
    
    question = TestQuestion.query.get_or_404(question_id)
    test_id = question.test_id
    
    if question.test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    db.session.delete(question)
    db.session.commit()
    
    return redirect(url_for('teacher_tests.edit_test', test_id=test_id))

@bp.route('/<int:test_id>/toggle_status', methods=['POST'])
@login_required
def toggle_test_status(test_id):
    """Test status activation/deactivation"""
    if not current_user.is_teacher:
        abort(403)
    
    test = Test.query.get_or_404(test_id)
    
    if test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    test.is_active = not test.is_active
    db.session.commit()
    
    return redirect(url_for('teacher_tests.my_tests'))

@bp.route('/<int:test_id>/results')
@login_required
def test_results(test_id):
    """Test results overview"""
    if not current_user.is_teacher:
        abort(403)
    
    test = Test.query.get_or_404(test_id)
    
    if test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    results = TestResult.query.filter_by(
        test_id=test_id, 
        status='completed'
    ).order_by(TestResult.completed_at.desc()).all()
    
    statistics = TestResult.get_test_statistics(test_id)
    
    return render_template('teacher/tests/test_results.html', 
                         test=test, 
                         results=results, 
                         statistics=statistics)

@bp.route('/<int:test_id>/delete', methods=['POST'])
@login_required
def delete_test(test_id):
    """Test deletion"""
    if not current_user.is_teacher:
        abort(403)
    
    test = Test.query.get_or_404(test_id)
    
    if test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    # Check if test has student results
    results_count = TestResult.query.filter_by(test_id=test_id).count()
    if results_count > 0:
        return "Cannot delete", 403
    
    db.session.delete(test)
    db.session.commit()
    
    return redirect(url_for('teacher_tests.my_tests'))