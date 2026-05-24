from functools import wraps
from flask import Blueprint, flash, redirect, request, session, url_for
from template_utils import stream_template

from auth_service import AuthError, sign_in_with_email_and_password, get_admin_profile
from config import ADMIN_ROLE

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('user_role') != ADMIN_ROLE:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)

    return wrapped


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        if not email or not password:
            flash('Email и пароль обязательны', 'error')
            return stream_template('auth/login.html')

        try:
            token_data = sign_in_with_email_and_password(email, password)
            profile = get_admin_profile(email, token_data.get('localId'))
            if not profile or profile.get('role') != ADMIN_ROLE:
                flash('Нет доступа администратора', 'error')
                return stream_template('auth/login.html')

            session['user_email'] = email
            session['user_uid'] = token_data.get('localId')
            session['id_token'] = token_data.get('idToken')
            session['user_role'] = profile.get('role')
            session['user_name'] = profile.get('name') or email
            return redirect(url_for('users.index'))
        except AuthError as exc:
            flash(str(exc), 'error')
        except Exception as exc:
            flash('Ошибка при входе: ' + str(exc), 'error')

    return stream_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
