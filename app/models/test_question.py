from app.extensions import db
from datetime import datetime

class TestQuestion(db.Model):
    """Test question model"""
    __tablename__ = 'test_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('open', 'multiple_choice'), nullable=False, default='open')
    points = db.Column(db.Integer, default=1, nullable=False)
    position = db.Column(db.Integer, default=1)
    correct_answer = db.Column(db.Text)  # Teisingas atsakymas atviriems klausimams
    
    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    
    # Relationships
    test = db.relationship('Test', back_populates='test_questions')
    test_answers = db.relationship('TestAnswer', back_populates='question')

    __table_args__ = (
        db.CheckConstraint('points > 0', name='positive_points'),
    )

    def __repr__(self):
        return f'<TestQuestion {self.id}: pos{self.position} - {self.question[:30]}...>'  # {self.question[:30]}...> tik pirmi 30 simbolių

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'question': self.question,
            'question_type': self.question_type,
            'points': self.points,
            'position': self.position, 
            'correct_answer': self.correct_answer if self.question_type == 'open' else None
        }


    def validate_question_data(self):
        """Validate question data"""
        errors = []
        
        if not self.question or len(self.question.strip()) < 5:
            errors.append("Question text must be at least 5 characters long")
        
        if self.points <= 0:
            errors.append("Points must be a positive integer")
        
        if self.position <= 0:
            errors.append("Position must be a positive integer")
        
        if self.question_type == 'open' and not self.correct_answer:
            errors.append("Open question must have a correct answer")
        
        return errors



    def check_answer(self, student_answer):
        """Check if student's answer is correct"""
        try:
            if self.question_type == 'open': # atviras klausimas
                if not student_answer or not self.correct_answer: # jei nėra atsakymo arba teisingo atsakymo
                    return False
                return self.correct_answer.strip().lower() == student_answer.strip().lower() # lyginam atsakymus be tarpų ir mažosiomis raidėmis
            return False
        except Exception as e:
            return False

    @staticmethod
    def get_questions_by_position(test_id):
        """Get questions ordered by position"""
        try: 
            return TestQuestion.query.filter_by(test_id=test_id)\
                .order_by(TestQuestion.position).all() #order_by, kad gautume klausimus pagal pozicija
        except Exception as e:
            return []

    @staticmethod
    def get_next_position(test_id):
        """Get next position for new question"""
        try:
            questions = TestQuestion.query.filter_by(test_id=test_id).all() # gaunam visus klausimus pagal test_id
            if len(questions) == 0: # jeigu nėra klausimų grąžinam 1
                return 1
            # Jei yra klausimų - rasti didžiausią poziciją ir pridėti 1
            biggest_position = 0 # pradedam nuo 0, kad galėtume rasti didžiausią poziciją
            for question in questions:
                if question.position > biggest_position: 
                    biggest_position = question.position
            
            return biggest_position + 1         #nauja pozicija bus didžiausia + 1
        except Exception as e:
            return 1                              #jei klaida, griztam i 1 pozicija

    def move_to_position(self, new_position):   # klausimo perkėlimas į naują poziciją
        """Move question to new position and adjust others"""
        try:
            if new_position <= 0:
                return False, "Position must be a positive integer"
                    
            old_position = self.position             # saugome seną poziciją
            if old_position == new_position: 
                return True, "Position is unchanged"
            
            # Perkeliam klausimą į naują poziciją ir atnaujinam kitų klausimų pozicijas
            questions = TestQuestion.query.filter_by(test_id=self.test_id)\
                .filter(TestQuestion.id != self.id).all()
            
            if old_position < new_position:
                # Perkeliam žemyn - sumažinam pozicijas tarp old ir new
                for q in questions:
                    if old_position < q.position <= new_position:
                        q.position -= 1
            else:
                # Perkeliam aukštyn - padidinam pozicijas tarp new ir old
                for q in questions:
                    if new_position <= q.position < old_position:
                        q.position += 1
            self.position = new_position # nustatom naują poziciją           
            db.session.commit()
            return True, f"Question moved to new {new_position} position"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error during move: {str(e)}"