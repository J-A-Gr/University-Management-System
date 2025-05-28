from flask import Blueprint, render_template

bp = Blueprint('errors', __name__)

@bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(e):
    return render_template('errors/500.html'), 500

@bp.app_errorhandler(413)
def file_too_large(e):
    return render_template('errors/413.html'), 413

@bp.route('/unauthorized')
def unauthorized():
    return render_template('unauthorized.html'), 403