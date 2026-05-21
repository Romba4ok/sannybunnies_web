from flask import Blueprint, redirect, render_template, request, url_for
from firebase_admin import firestore

from config import UPLOAD_FOLDER
from firebase_admin_service import (
    create_document,
    delete_document,
    get_children_with_parent,
    get_collection_items,
    get_document,
    get_users_by_role,
    set_document,
    update_child,
    update_document,
    update_user_password,
    remove_child_from_group,
    upload_photo_to_storage,
)
from routes.auth import login_required
from auth_service import create_user_with_email_and_password

users_bp = Blueprint('users', __name__, template_folder='../templates')


def _save_photo(file, folder_path):
    if file and file.filename:
        return upload_photo_to_storage(file, folder_path)
    return None


@users_bp.route('/')
@login_required
def index():
    admins = get_users_by_role('admin')
    teachers = get_users_by_role('teacher')
    parents = get_users_by_role('parent')
    children = get_children_with_parent()
    return render_template('users/users.html', admins=admins, teachers=teachers, parents=parents, children=children, section='Пользователи')


@users_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name', 'Новый пользователь').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    role = request.form.get('role', 'user').strip()
    password = request.form.get('password', '').strip()
    photo = request.files.get('photo')
    photo_url = _save_photo(photo, 'profile_photos') if photo else None
    if email and password:
        try:
            user = create_user_with_email_and_password(email, password)
            uid = user.get('localId') or user.get('uid')
            user_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'role': role,
                'uid': uid,
                'notificationsEnabled': False,
                'platform': 'email',
                'createdAt': firestore.SERVER_TIMESTAMP,
            }
            if photo_url:
                user_data['photoUrl'] = photo_url
            set_document('users', uid, user_data)
        except Exception:
            pass
    return redirect(url_for('users.index'))


@users_bp.route('/edit/<user_id>', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', '').strip()
        password = request.form.get('password', '').strip()
        photo = request.files.get('photo')
        photo_url = _save_photo(photo, 'profile_photos') if photo else None
        update_data = {'name': name, 'email': email, 'phone': phone, 'role': role}
        if photo_url:
            update_data['photoUrl'] = photo_url
        user = get_document('users', user_id)
        if password and user:
            update_user_password(user.get('uid'), password)
        update_document('users', user_id, update_data)
        return redirect(url_for('users.index'))

    user = get_document('users', user_id)
    return render_template('users/edit_user.html', user=user)


@users_bp.route('/delete/<user_id>', methods=['POST'])
@login_required
def delete(user_id):
    delete_document('users', user_id)
    return redirect(url_for('users.index'))


@users_bp.route('/<parent_id>/edit_child/<child_id>', methods=['GET', 'POST'])
@users_bp.route('/edit_child/<child_id>', methods=['GET', 'POST'])
@login_required
def edit_child(child_id, parent_id=None):
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        gender = request.form.get('gender', '').strip()
        health_text = request.form.get('health_text', '').strip()
        mood = request.form.get('mood', '').strip()
        features = [f.strip() for f in request.form.get('features', '').split(',') if f.strip()] if request.form.get('features') else []
        in_kindergarten = request.form.get('in_kindergarten') == 'on'
        group_id = request.form.get('group_id') or None
        request_status = bool(group_id)

        child_doc = get_document('children', child_id)
        if not parent_id:
            parent_id = child_doc.get('parent_id') if child_doc else None
        photo = request.files.get('photo')
        photo_url = _save_photo(photo, f'child_photos/{parent_id}') if photo else None

        child = get_document('children', child_id)
        old_group_id = child.get('group_id') if child else None

        if old_group_id and old_group_id != group_id:
            remove_child_from_group(old_group_id, child_id)

        if group_id and group_id != old_group_id:
            group = get_document('groups', group_id)
            children_ids = group.get('children_uids', []) or []
            if child_id not in children_ids:
                children_ids.append(child_id)
            update_document('groups', group_id, {'children_uids': children_ids})

        update_data = {
            'name': name,
            'birthDate': birth_date,
            'gender': gender,
            'healthText': health_text,
            'mood': mood,
            'features': features,
            'inKindergarten': in_kindergarten,
            'requestStatus': request_status,
            'group_id': group_id,
        }
        if photo_url:
            update_data['photoUrl'] = photo_url

        update_child(child_id, update_data)
        return redirect(url_for('users.index'))

    child = get_document('children', child_id)
    groups = get_collection_items('groups')
    if not parent_id:
        parent_id = child.get('parent_id') if child else None
    return render_template('users/edit_child.html', child=child, parent_id=parent_id, groups=groups)
