from app.extensions import db
from datetime import datetime

class TestAnswer(db.Model):
    """Individual answers to test questions"""
    __tablename__ = 'test_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    answer_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    answered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    test_result_id = db.Column(db.Integer, db.ForeignKey('test_results.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('test_questions.id'), nullable=False)
    

    test_result = db.relationship('TestResult', back_populates='answers')
    question = db.relationship('TestQuestion', back_populates='test_answers')

    __table_args__ = (          #uztikrinti, kad studentas negali atsakyti į tą patį klausimą kelis kartus
        db.UniqueConstraint('test_result_id', 'question_id', name='unique_answer_per_question'),
    )

    def __repr__(self): 
        return f'<TestAnswer {self.id}: Q{self.question_id} - {"✓" if self.is_correct else "✗"}>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'answer_text': self.answer_text,
            'is_correct': self.is_correct,
            'answered_at': self.answered_at.isoformat() if self.answered_at else None,
            'question_id': self.question_id,
            'test_result_id': self.test_result_id
        }

    def check_and_save_answer(self):
        """Check if answer is correct and save"""
        try:
            if self.question:
                self.is_correct = self.question.check_answer(self.answer_text)
                db.session.commit()
                return True
        except Exception as e:
            db.session.rollback()
            return False