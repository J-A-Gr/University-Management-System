from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort, flash
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Test, TestResult, TestAnswer, TestQuestion, ModuleEnrollment
from app.forms.test_forms import TestCompletionForm
from app.extensions import db

bp = Blueprint('student_tests', __name__, url_prefix='/student/tests')

@bp.route('/')
@login_required
def available_tests():
    """Available tests for student"""
    if not current_user.is_student:
        abort(403)
    
    # Gaunam visus studento modulius, kuriuose jis yra aktyvus
    enrollments = ModuleEnrollment.query.filter_by(
        student_info_id=current_user.student_info.id,
        status='active'
    ).all()
    
    available_tests = []
    for enrollment in enrollments:
        module_tests = Test.query.filter_by(
            module_id=enrollment.module_id, 
            is_active=True
        ).all()
        
        for test in module_tests:
            can_take, message = test.can_student_take_test(current_user.id)
            attempts = test.get_student_attempts(current_user.id)
            
            available_tests.append({
                'test': test,
                'module_name': enrollment.module.name,
                'can_take': can_take,
                'message': message,
                'attempts_count': len(attempts),
                'max_attempts': test.max_attempts,
                'best_result': max(attempts, key=lambda x: x.percentage) if attempts else None
            })
    
    return render_template('student/tests/available_tests.html', available_tests=available_tests)

@bp.route('/<int:test_id>/start')
@login_required
def start_test(test_id):
    """Test start"""
    if not current_user.is_student:
        abort(403)
    
    test = Test.query.get_or_404(test_id)
    
    can_take, message = test.can_student_take_test(current_user.id)
    if not can_take:
        abort(403)
    

    test_result = TestResult( # kuriamas naujas testų rezultatas
        test_id=test_id,
        user_id=current_user.id,
        max_possible_score=test.get_total_points(),
        percentage=0,
        status='in_progress'
    )
    
    db.session.add(test_result)
    db.session.commit()
    
    return redirect(url_for('student_tests.take_test', result_id=test_result.id))

@bp.route('/take/<int:result_id>')
@login_required
def take_test(result_id):
    """Take test"""
    if not current_user.is_student:
        abort(403)
    
    test_result = TestResult.query.get_or_404(result_id)
    
    # tikrinam ar studentas gali tęsti testą
    if test_result.user_id != current_user.id:
        abort(403)
    
    if test_result.status == 'completed':
        return redirect(url_for('student_tests.test_result', result_id=result_id))
    
    questions = TestQuestion.get_questions_by_position(test_result.test_id)
    
    # Gaunam esamus atsakymus
    existing_answers = {
        answer.question_id: answer.answer_text 
        for answer in test_result.answers
    }
    
    completion_form = TestCompletionForm()
    
    return render_template('student/tests/take_test.html', 
                         test_result=test_result, 
                         questions=questions,
                         existing_answers=existing_answers,
                         completion_form=completion_form)


@bp.route('/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    """Answer submission (AJAX)"""
    if not current_user.is_student:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    result_id = data.get('result_id')
    question_id = data.get('question_id')
    answer_text = data.get('answer_text', '').strip()
    
    if not all([result_id, question_id]):
        return jsonify({'error': 'Missing data'}), 400
    
    test_result = TestResult.query.get(result_id)
    if not test_result or test_result.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if test_result.status != 'in_progress':
        return jsonify({'error': 'Test completed'}), 400
    
    # tikrinam ar jau yra atsakymas
    existing = TestAnswer.query.filter_by(
        test_result_id=result_id,
        question_id=question_id
    ).first()
    
    if existing:
        existing.answer_text = answer_text
        existing.check_and_save_answer()
    else:
        answer = TestAnswer(
            test_result_id=result_id,
            question_id=question_id,
            answer_text=answer_text
        )
        answer.check_and_save_answer()
        db.session.add(answer)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Answer saved'})


@bp.route('/complete/<int:result_id>', methods=['POST'])
@login_required
def complete_test(result_id):
    """Test completion"""
    if not current_user.is_student:
        abort(403)
    
    test_result = TestResult.query.get_or_404(result_id)
    
    if test_result.user_id != current_user.id:
        abort(403)
    
    if test_result.status == 'completed':
        return redirect(url_for('student_tests.test_result', result_id=result_id))
    
    form = TestCompletionForm()
    if form.validate_on_submit():
        success, message = test_result.complete_test()
        if success:
            print(f"Test completed successfully: {message}")
            try:
                integration_success, integration_message = test_result.integrate_with_module_grade()
                if integration_success:
                    print(f"Integration SUCCESS: {integration_message}")
                else:
                    print(f"Integration FAILED: {integration_message}")
            except Exception as e:
                print(f"Integration ERROR: {str(e)}")
            
            return redirect(url_for('student_tests.test_result', result_id=result_id))
        else:
            print(f"Test completion failed: {message}")
    else:
        print("Form validation failed")
    
    return redirect(url_for('student_tests.take_test', result_id=result_id))



@bp.route('/result/<int:result_id>')
@login_required
def test_result(result_id):
    """Test result view"""
    if not current_user.is_student:
        abort(403)
    
    test_result = TestResult.query.get_or_404(result_id)
    
    if test_result.user_id != current_user.id:
        abort(403)
    
    # Gaunam klausimus ir atsakymus
    questions_with_answers = []
    questions = TestQuestion.get_questions_by_position(test_result.test_id)
    
    for question in questions:
        answer = TestAnswer.query.filter_by(
            test_result_id=result_id,
            question_id=question.id
        ).first()
        
        questions_with_answers.append({
            'question': question,
            'student_answer': answer.answer_text if answer else 'No answer',
            'is_correct': answer.is_correct if answer else False,
            'correct_answer': question.correct_answer if test_result.test.show_results_immediately else None
        })
    
    return render_template('student/tests/test_result.html', 
                         test_result=test_result,
                         questions_with_answers=questions_with_answers)

@bp.route('/my_results')
@login_required
def my_results():
    """Student test results list"""
    if not current_user.is_student:
        abort(403)
    
    results = TestResult.get_user_results(current_user.id)
    return render_template('student/tests/my_results.html', results=results)