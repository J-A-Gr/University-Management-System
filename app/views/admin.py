from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user
from app.extensions import db
from app.utils.decorators import admin_required
from app.models import User
from sqlalchemy import func
from app.forms.admin import EmptyForm

bp = Blueprint('admin', __name__)


@bp.route('/admin/panel')
@admin_required
def admin_panel():
    """Admin dashboard"""
    form = EmptyForm()
    search = request.args.get('search', '').strip()  # paieškos laukui naudojama, (Kai forma siunčiama su GET)

    query = User.query

    # papildomas filtravimas
    if search:
        search_pattern = f"%{search.lower()}%"
        query = query.filter( db.func.lower(User.email).like(search_pattern)) # WHERE LOWER(email) LIKE '%email@...@%'

    # Adminai viršuje, paprasti useriai sekantys.
    users = query.order_by(User.is_admin.desc(), User.username.asc()).all()

    return render_template('admin/panel.html', title='Admin Panel', users=users, search=search, form=form)


@bp.route('/promote/<int:user_id>', methods=['POST'])
@admin_required
def promote_user(user_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)

        if user.is_admin:
            flash(f"User '{user.username}' is already an admin.", "error")
        else:
            user.is_admin = True
            db.session.commit()
            flash(f"User '{user.username}' has been promoted to admin.", "success")

    return redirect(url_for('admin.admin_panel'))

@bp.route('/demote/<int:user_id>', methods=['POST'])
@admin_required
def demote_user(user_id):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(user_id)

        # Apsauga nuo hardcodinto admino pašalinimo.
        if user.email == "admin@example.com":
            flash("Cannot demote the 'super' admin.", "error") 
            return redirect(url_for('admin.admin_panel'))
        
        if not user.is_admin:
            flash(f"User '{user.username}' is not an admin.", "error")
        else:
            user.is_admin = False
            db.session.commit()
            flash(f"User '{user.username}' has been demoted from admin.", "success")

    return redirect(url_for('admin.admin_panel'))