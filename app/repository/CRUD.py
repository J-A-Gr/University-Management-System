### Čia reikia padaryti informacijos įrašymą, atnaujinimą, ištrynimą ir gavimą iš duomenų bazės
### Dabartinis sugeneruotas AI, tikriausiai nieko gero nedaro! :DDD 
### DB CRUD operations

from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy import func
from app.models.user import User
from app.models.student_info import StudentInfo 
from app.models.teacher_info import TeacherInfo

from app.models.study_program import StudyProgram

def create_student_info(student_data):


def create_user(user_data):
    """Create a new user in the database."""
    try:
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def update_user(user_id, user_data):
    """Update an existing user in the database."""
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        for key, value in user_data.items():
            setattr(user, key, value)
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def delete_user(user_id):
    """Delete a user from the database."""
    try:
        user = User.query.get(user_id)
        if not user:
            return None
        db.session.delete(user)
        db.session.commit()
        return user
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e

def get_user(user_id):
    """Get a user by ID from the database."""
    try:
        return User.query.get(user_id)
    except SQLAlchemyError as e:
        raise e

def get_all_users():
    """Get all users from the database."""
    try:
        return User.query.all()
    except SQLAlchemyError as e:
        raise e

def get_user_count():
    """Get the total number of users in the database."""
    try:
        return db.session.query(func.count(User.id)).scalar()
    except SQLAlchemyError as e:
        raise e


