from app.extensions import db
from datetime import datetime

class TestQuestion(db.Model):
    """Test question model - tik multiple choice su 4 variantais"""
    __tablename__ = 'test_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    
    points = db.Column(db.Integer, default=1, nullable=False)
    position = db.Column(db.Integer, default=1, nullable=False)
    
            # 4 atsakymų variantai
    choice_a = db.Column(db.String(500), nullable=False)
    choice_b = db.Column(db.String(500), nullable=False)
    choice_c = db.Column(db.String(500), nullable=False)
    choice_d = db.Column(db.String(500), nullable=False)
    
                # Teisingas atsakymas - tik A, B, C arba D
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C' arba 'D'
    
  
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)

    test = db.relationship('Test', back_populates='test_questions')
    test_answers = db.relationship('TestAnswer', back_populates='question', cascade='all, delete-orphan')

    __table_args__ = (
        db.CheckConstraint('points > 0', name='positive_points'),
        db.CheckConstraint('position > 0', name='positive_position'),
        db.CheckConstraint("correct_answer IN ('A', 'B', 'C', 'D')", name='valid_correct_answer'),
    )

    def __repr__(self):
        return f'<TestQuestion {self.id}: pos{self.position} - {self.question[:30]}...>'


    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'question': self.question,
            'points': self.points,
            'position': self.position,
            'choices': {
                'A': self.choice_a,
                'B': self.choice_b,
                'C': self.choice_c,
                'D': self.choice_d
            },
            'correct_answer': self.correct_answer,
            'test_id': self.test_id
        }

    def get_choices_list(self):
        """Get choices as list for templates"""
        return [
            {'letter': 'A', 'text': self.choice_a},
            {'letter': 'B', 'text': self.choice_b},
            {'letter': 'C', 'text': self.choice_c},
            {'letter': 'D', 'text': self.choice_d}
        ]

    def validate_question_data(self):
        """Validate question data"""
        errors = []
        
        if not self.question or len(self.question.strip()) < 5:
            errors.append("Question text must be at least 5 characters long")
        
        if self.points <= 0:
            errors.append("Points must be a positive integer")
        
        if self.position <= 0:
            errors.append("Position must be a positive integer")
        
        # Tikriname ar visi choices užpildyti
        if not all([self.choice_a, self.choice_b, self.choice_c, self.choice_d]):
            errors.append("All four answer choices must be provided")
        
        # Tikriname ar choices nėra per trumpi
        choices = [self.choice_a, self.choice_b, self.choice_c, self.choice_d]
        for i, choice in enumerate(choices):
            if len(choice.strip()) < 1:
                errors.append(f"Choice {chr(65+i)} cannot be empty")
        
        # Tikriname correct_answer
        if self.correct_answer not in ['A', 'B', 'C', 'D']:
            errors.append("Correct answer must be A, B, C, or D")
        
        return errors

    def check_answer(self, student_answer):
        """Check if student's answer is correct"""
        try:
            if not student_answer:
                return False
            return student_answer.strip().upper() == self.correct_answer.upper()
        except Exception as e:
            return False

    @staticmethod
    def get_questions_by_position(test_id):
        """Get questions ordered by position"""
        try:
            return TestQuestion.query.filter_by(test_id=test_id)\
                .order_by(TestQuestion.position).all()
        except Exception as e:
            return []

    @staticmethod
    def get_next_position(test_id):
        """Get next position for new question"""
        try:
            last_question = TestQuestion.query.filter_by(test_id=test_id)\
                .order_by(TestQuestion.position.desc()).first()
            
            if last_question:
                return last_question.position + 1
            return 1
        except Exception as e:
            return 1

    def move_to_position(self, new_position):
        """Move question to new position and adjust others"""
        try:
            if new_position <= 0:
                return False, "Position must be a positive integer"
            
            old_position = self.position
            if old_position == new_position:
                return True, "Position is unchanged"
            
            # Get all other questions in this test
            questions = TestQuestion.query.filter_by(test_id=self.test_id)\
                .filter(TestQuestion.id != self.id).all()
            
            if old_position < new_position:
                # Moving down - decrease positions between old and new
                for q in questions:
                    if old_position < q.position <= new_position:
                        q.position -= 1
            else:
                # Moving up - increase positions between new and old
                for q in questions:
                    if new_position <= q.position < old_position:
                        q.position += 1
            
            self.position = new_position
            db.session.commit()
            return True, f"Question moved to position {new_position}"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error during move: {str(e)}"

    def get_correct_choice_text(self):
        """Get the text of the correct answer choice"""
        choice_map = {
            'A': self.choice_a,
            'B': self.choice_b,
            'C': self.choice_c,
            'D': self.choice_d
        }
        return choice_map.get(self.correct_answer, "Unknown")

    def duplicate_to_test(self, target_test_id):
        """Duplicate this question to another test"""
        try:
            new_question = TestQuestion(
                question=self.question,
                points=self.points,
                choice_a=self.choice_a,
                choice_b=self.choice_b,
                choice_c=self.choice_c,
                choice_d=self.choice_d,
                correct_answer=self.correct_answer,
                test_id=target_test_id,
                position=TestQuestion.get_next_position(target_test_id)
            )
            
            db.session.add(new_question)
            db.session.commit()
            return True, "Question duplicated successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error duplicating question: {str(e)}"

    @staticmethod
    def bulk_update_positions(test_id, question_ids_in_order):
        """Update positions for multiple questions at once"""
        try:
            for new_position, question_id in enumerate(question_ids_in_order, 1):
                question = TestQuestion.query.get(question_id)
                if question and question.test_id == test_id:
                    question.position = new_position
            
            db.session.commit()
            return True, "Positions updated successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error updating positions: {str(e)}"

    def is_answered_by_student(self, student_id):
        """Check if this question was answered by specific student"""
        from app.models.test_answer import TestAnswer
        from app.models.test_result import TestResult
        
        return TestAnswer.query.join(TestResult).filter(
            TestAnswer.question_id == self.id,
            TestResult.user_id == student_id
        ).first() is not None