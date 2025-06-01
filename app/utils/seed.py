from app.models.user import User
from app.extensions import db, bcrypt
from sqlalchemy import inspect
from datetime import datetime

def create_hardcoded_admin():
    """Creates a default admin user if 'users' table exists and no such user is found."""
    inspector = inspect(db.engine)

    if 'users' not in inspector.get_table_names():
        print("'users' table does not exist. Skipping hardcoded admin creation.")
        return

    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            email='admin@example.com',
            password_hash=bcrypt.generate_password_hash('Admin123+').decode('utf-8'),
            is_admin=True,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print("Hardcoded admin created.")
    else:
        print("Hardcoded admin already exists.")
###################################################################################################
# for test purposes, leave commented out.

# def create_hardcoded_student():
#     inspector = inspect(db.engine)

#     if 'users' not in inspector.get_table_names():
#         print("'users' table does not exist. Skipping hardcoded admin creation.")
#         return

#     if not User.query.filter_by(email='student@example.com').first():
#         admin = User(
#             email='student@example.com',
#             password_hash=bcrypt.generate_password_hash('Admin123+').decode('utf-8'),
#             is_student=True,
#             first_name = 'Juonis',
#             last_name = 'Hardkodas',
#             is_active=True,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )
#         db.session.add(admin)
#         db.session.commit()
#         print("Hardcoded student created.")
#     else:
#         print("Hardcoded student already exists.")
        
# def create_hardcoded_teacher():
#     inspector = inspect(db.engine)

#     if 'users' not in inspector.get_table_names():
#         print("'users' table does not exist. Skipping hardcoded admin creation.")
#         return

#     if not User.query.filter_by(email='teacher@example.com').first():
#         admin = User(
#             email='teacher@example.com',
#             password_hash=bcrypt.generate_password_hash('Admin123+').decode('utf-8'),
#             is_teacher=True,
#             first_name = 'Jan',
#             last_name = 'Ivanas',
#             is_active=True,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )
#         db.session.add(admin)
#         db.session.commit()
#         print("Hardcoded teacher created.")
#     else:
#         print("Hardcoded teacher already exists.")

