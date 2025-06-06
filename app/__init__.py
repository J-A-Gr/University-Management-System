from flask import Flask
from app.extensions import db, migrate, login_manager, csrf
from app.config import Config
from app.models.user import User
#from app.utils.seed import create_hardcoded_admin # create_hardcoded_student, create_hardcoded_teacher
#Šitą pakeičiau, kad nekurtų hardcoded admin, nes gaunu ciklinį importą, 
#Padariau testing_data.py, kurį reikia pasileisti prieš run.py ir jis sukuria adminą ir kitus (jei reiks tik admino kitus užkomentuokit ;)).
import os
from app.utils.seed_data import seed_data

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # įsitikiname, kad upload folderis egzistuoja(profile_pic)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from app.views.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.views.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.views.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.views.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.views.student import bp as student_bp
    app.register_blueprint(student_bp, url_prefix='/student')

    from app.views.teacher import bp as teacher_bp
    app.register_blueprint(teacher_bp, url_prefix='/teacher')

    from app.views.error_handlers import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.views.teacher_tests import bp as teacher_tests_bp
    app.register_blueprint(teacher_tests_bp)

    from app.views.student_tests import bp as student_tests_bp
    app.register_blueprint(student_tests_bp)

    from app.views.modules import bp as modules_bp
    app.register_blueprint(modules_bp, url_prefix='/modules')

    from app.views.assessments import bp as assessments_bp
    app.register_blueprint(assessments_bp)
    

    # hardcoded admin
    # with app.app_context():
    #     create_hardcoded_admin()
        # create_hardcoded_student() # FOR TEST PURPOSES
        # create_hardcoded_teacher() # FOR TEST PURPOSES
    
    return app 
    