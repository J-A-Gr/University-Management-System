from flask import Blueprint, current_app, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app.config import Config
from app.forms.main import ProfileForm
from app.extensions import db
from app.utils.helpers import allowed_file
import os
import uuid

bp = Blueprint('api', __name__)


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()

    if form.validate_on_submit():
        # atnaujinam userio field'us
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data

        # profilio nuotraukos įkėlimas.
        file = form.profile_picture.data
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
            file.save(file_path)

            # ištrinam seną failą, jeigu ne default
            if current_user.profile_picture and current_user.profile_picture != 'default.png':
                try:
                    os.remove(os.path.join(Config.UPLOAD_FOLDER, current_user.profile_picture))
                except Exception as e:
                    print("Could not delete old picture:", e)

            current_user.profile_picture = unique_filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('api.edit_profile'))  #  pataisytas blueprint api

    elif request.method == 'GET':
        # Pre-fill form for GET requests
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email

    return render_template('auth/edit_profile.html', form=form)
