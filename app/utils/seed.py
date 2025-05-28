from app.models.user import User
from app.extensions import db, bcrypt
from datetime import datetime

def create_hardcoded_admin():
    """Creates a default admin user if none exists."""
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