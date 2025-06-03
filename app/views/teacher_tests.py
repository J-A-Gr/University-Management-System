from flask import Blueprint, render_template, redirect, url_for, abort, flash, request
from flask_login import login_required, current_user
from app.models import Test, TestQuestion, Module, Assessment, TestResult
from app.forms.test_forms import TestForm, QuestionForm, TestEditForm, TestCompletionForm
from app.extensions import db

bp = Blueprint('teacher_tests', __name__, url_prefix='/teacher/tests')

@bp.route('/')
@login_required
def my_tests():
    """Teacher's tests overview"""
    if not current_user.teacher_info:
        current_user.ensure_teacher_info()
        db.session.commit()
    
    tests = Test.query.filter_by(
        created_by_teacher_id=current_user.teacher_info.id
    ).order_by(Test.created_at.desc()).all()
    
    return render_template('teacher/tests/my_tests.html', tests=tests)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_test():
    """New test creation - PATAISYTA"""
    if not current_user.is_teacher:
        abort(403)
    
    form = TestForm(teacher_id=current_user.teacher_info.id)
    
    # Tikrinam, ar yra atsiskaitymu, kuriems galima sukurti testus
    if not form.assessment_id.choices:
        flash('Nėra atsiskaitymų, kuriems galima sukurti testus. Pirmiausia sukurkite atsiskaitymus.', 'info')
        return redirect(url_for('assessments.list_assessments'))
    
    if form.validate_on_submit():
        assessment = Assessment.query.get(form.assessment_id.data)
        if not assessment or assessment.module.teacher_id != current_user.teacher_info.id:
            abort(403)
        
        # Tikrinam ar nėra testo atsiskaitymui
        if assessment.tests:
            flash('Šis atsiskaitymas jau turi testą!', 'error')
            return redirect(url_for('teacher_tests.my_tests'))
        
        test = Test(
            title=form.title.data,
            description=form.description.data,
            time_limit=form.time_limit.data,
            max_attempts=form.max_attempts.data,
            show_results_immediately=True,
            stop_after_pass=True,
            assessment_id=form.assessment_id.data, 
            module_id=assessment.module_id,
            created_by_teacher_id=current_user.teacher_info.id
        )
        
        db.session.add(test)
        db.session.commit()
        
        flash(f'Testas sukurtas atsiskaitymui "{assessment.title}"!', 'success')
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
    question_form = QuestionForm()
    edit_form = TestEditForm(obj=test)
    
    return render_template('teacher/tests/edit_test.html', 
                         test=test, 
                         questions=questions, 
                         question_form=question_form,
                         edit_form=edit_form)

@bp.route('/<int:test_id>/add_question', methods=['POST'])
@login_required
def add_question(test_id):
    """SUPAPRASTINTA klausimo pridėjimas - tik multiple choice"""
    if not current_user.is_teacher:
        abort(403)
    
    test = Test.query.get_or_404(test_id)
    
    if test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    form = QuestionForm()
    
    if form.validate_on_submit():
        try:
            question = TestQuestion(
                question=form.question.data,
                points=form.points.data,
                choice_a=form.choice_a.data,
                choice_b=form.choice_b.data,
                choice_c=form.choice_c.data,
                choice_d=form.choice_d.data,
                correct_answer=form.correct_answer.data,
                test_id=test_id,
                position=TestQuestion.get_next_position(test_id)
            )
            
            db.session.add(question)
            db.session.commit()
            
            flash('Klausimas sėkmingai pridėtas!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Klaida pridedant klausimą: {str(e)}', 'error')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('teacher_tests.edit_test', test_id=test_id))

@bp.route('/<int:test_id>/update', methods=['POST'])
@login_required
def update_test(test_id):
    """Test update"""
    if not current_user.is_teacher:
        abort(403)
    
    test = Test.query.get_or_404(test_id)
    
    if test.created_by_teacher_id != current_user.teacher_info.id:
        abort(403)
    
    form = TestEditForm()
    
    if form.validate_on_submit():
        test.title = form.title.data
        test.description = form.description.data
        test.time_limit = form.time_limit.data
        test.max_attempts = form.max_attempts.data
        
        db.session.commit()
        flash('Testas atnaujintas!', 'success')
    
    return redirect(url_for('teacher_tests.edit_test', test_id=test_id))

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
    
    flash('Klausimas ištrintas', 'info')
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
    
    status = 'aktyvus' if test.is_active else 'neaktyvus'
    flash(f'Testas dabar {status}', 'info')
    
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
    
         # tikrinam ar yra studentų rezultatų
    results_count = TestResult.query.filter_by(test_id=test_id).count()
    if results_count > 0:
        flash('Negalima ištrinti testo su studentų rezultatais', 'error')
        return redirect(url_for('teacher_tests.my_tests'))
    
    db.session.delete(test)
    db.session.commit()
    
    flash('Testas ištrintas', 'info')
    return redirect(url_for('teacher_tests.my_tests'))