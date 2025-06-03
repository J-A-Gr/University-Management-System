from app.extensions import db
from datetime import datetime

class TestAnswer(db.Model):
    """Studento atsakymas į testų klausimą"""
    __tablename__ = 'test_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    
    answer_text = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C' arba 'D'
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    test_result_id = db.Column(db.Integer, db.ForeignKey('test_results.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('test_questions.id'), nullable=False)
    

    test_result = db.relationship('TestResult', back_populates='answers')
    question = db.relationship('TestQuestion', back_populates='test_answers')

    __table_args__ = (
        db.UniqueConstraint('test_result_id', 'question_id', name='unique_answer_per_question'),
        db.CheckConstraint("answer_text IN ('A', 'B', 'C', 'D')", name='valid_answer_choice'),
    )

    def __repr__(self):
        return f'<TestAnswer {self.id}: Q{self.question_id} = {self.answer_text} {"✓" if self.is_correct else "✗"}>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'answer_text': self.answer_text,
            'is_correct': self.is_correct,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None,
            'question_id': self.question_id,
            'test_result_id': self.test_result_id,
            'question_text': self.question.question if self.question else None,
            'correct_answer': self.question.correct_answer if self.question else None
        }

    def check_and_save_answer(self):
        """Check if answer is correct and save - SUPAPRASTINTA"""
        try:
            if self.question:
                     # Tiesiog palyginam A, B, C, D
                self.is_correct = (self.answer_text.upper() == self.question.correct_answer.upper())
                db.session.commit()
                return True
        except Exception as e:
            db.session.rollback()
            return False

    def get_answer_text_full(self):
        """Get full answer text (not just letter)"""
        if not self.question:
            return self.answer_text
        
        choice_map = {
            'A': self.question.choice_a,
            'B': self.question.choice_b,
            'C': self.question.choice_c,
            'D': self.question.choice_d
        }
        return choice_map.get(self.answer_text.upper(), self.answer_text)

    @staticmethod
    def create_answer(test_result_id, question_id, answer_letter):
        """Create new answer"""
        try:
            existing = TestAnswer.query.filter_by(
                test_result_id=test_result_id,
                question_id=question_id
            ).first()
            
            if existing:
                existing.answer_text = answer_letter.upper() 
                existing.answered_at = datetime.utcnow() 
                existing.check_and_save_answer()
                return existing
            else:
                answer = TestAnswer(
                    test_result_id=test_result_id,
                    question_id=question_id,
                    answer_text=answer_letter.upper()
                )
                answer.check_and_save_answer()
                db.session.add(answer)
                db.session.commit()
                return answer
                
        except Exception as e:
            db.session.rollback()
            return None