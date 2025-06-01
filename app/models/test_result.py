from app.extensions import db
from datetime import datetime

class TestResult(db.Model):
    """Test result model for storing student test attempts"""
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    total_score = db.Column(db.Integer, default=0, nullable=False)
    max_possible_score = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum('in_progress', 'completed', 'submitted'), default='in_progress', nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    time_taken = db.Column(db.Integer)  # sekundėmis
    

    test_id = db.Column(db.Integer, db.ForeignKey('tests.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
    # Relationships
    test = db.relationship('Test', back_populates='test_results')
    user = db.relationship('User', back_populates='test_results')
    answers = db.relationship('TestAnswer', back_populates='test_result', cascade='all, delete-orphan')

    __table_args__ = (
        db.CheckConstraint('total_score >= 0', name='non_negative_score'), # negali būti neigiama
        db.CheckConstraint('max_possible_score > 0', name='positive_max_score'), # maksimalus balas turi būti teigiamas
        db.CheckConstraint('percentage >= 0 AND percentage <= 100', name='valid_percentage'), #procentas turi būti tarp 0 ir 100
    )

    def __repr__(self):
        return f'<TestResult {self.id}: User{self.user_id} Test{self.test_id} - {self.percentage}%>'

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'total_score': self.total_score,
            'max_possible_score': self.max_possible_score,
            'percentage': self.percentage,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'time_taken': self.time_taken,
            'test_id': self.test_id,
            'user_id': self.user_id
        }

    def calculate_score(self):
        """Calculate total score from answers"""
        try:
            total = 0
            for answer in self.answers:
                if answer.is_correct:
                    total += answer.question.points
            
            self.total_score = total
            self.percentage = (total / self.max_possible_score * 100) if self.max_possible_score > 0 else 0 
            return True
        except Exception as e:
            return False

    def is_completed(self):
        """Check if test attempt is completed"""
        return self.status == 'completed'

    def calculate_grade(self):
        """Calculate grade (1-10 scale) based on percentage"""
        if self.percentage >= 90: return 10
        elif self.percentage >= 80: return 9
        elif self.percentage >= 70: return 8
        elif self.percentage >= 60: return 7
        elif self.percentage >= 50: return 6
        elif self.percentage >= 40: return 5
        elif self.percentage >= 30: return 4
        elif self.percentage >= 20: return 3
        elif self.percentage >= 10: return 2
        else: return 1



    def complete_test(self):
        """Mark test as completed and calculate final score"""
        try:
            # pasitikrinam ar testas jau baigtas
            if self.status == 'completed': 
                return True, "Test already completed"
            
            # Nustatom kada baigtas
            self.completed_at = datetime.utcnow()
            self.status = 'completed'
            
            # susiskaiciuojam kiek laiko užtruko
            if self.started_at:
                time_difference = self.completed_at - self.started_at
                self.time_taken = int(time_difference.total_seconds())
            
            # Suskaičiuojam galutinį balą
            score_calculated = self.calculate_score()
            if not score_calculated:
                db.session.rollback()
                return False, "Error calculating final score"
            
            db.session.commit()
            return True, "Test completed successfully"
            
        except Exception as e:
            db.session.rollback()
            return False, f"Error completing test: {str(e)}"
        


    @staticmethod
    def get_user_results(user_id):
        """Get all test results for a specific user"""
        try:
            #filtruojam pagal user_id ir grąžinam rezultatus, surikiuotus pagal pradžios laiką
            return TestResult.query.filter_by(user_id=user_id)\
                .order_by(TestResult.started_at.desc()).all() 
        except Exception as e:
            return []

    @staticmethod
    def get_test_statistics(test_id): 
        """Get statistics for a specific test"""
        try:
            results = TestResult.query.filter_by(test_id=test_id, status='completed').all() # filtruojam pagal test_id ir statusą 'completed'
            if not results:
                return None
            
            scores = [r.percentage for r in results]
            return {
                'total_attempts': len(results),
                'average_score': sum(scores) / len(scores),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'pass_rate': len([s for s in scores if s >= 40]) / len(scores) * 100  # sukaičiuojam procentą tų, kurie gavo 40% ar daugiau
            }
        except Exception as e:
            return None


