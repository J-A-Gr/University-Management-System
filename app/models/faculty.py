from app.extensions import db

class Faculty(db.Model):
    """Faculty model for organizing teachers and study programs (BONUS POINTS)"""
    __tablename__ = 'faculties'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(100), nullable=False, unique=True)  # "Informatikos fakultetas"
    code = db.Column(db.String(10), nullable=False, unique=True) 