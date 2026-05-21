from flask import Blueprint, redirect, render_template, request, url_for
from firebase_admin import firestore

from firebase_admin_service import (
    get_children_with_parent,
    get_collection_items,
    get_document,
    set_child_group_id,
    update_child,
    update_document,
    create_child,
    upload_photo_to_storage,
)
from routes.auth import login_required

requests_bp = Blueprint('requests', __name__, template_folder='../templates')


def _save_photo(file):
    if file and file.filename:
        return upload_photo_to_storage(file, 'request_photos')
    return None


@requests_bp.route('/')
@login_required
def index():
    children = get_children_with_parent()
    pending_requests = [child for child in children if child.get('requestStatus') is None]
    groups = get_collection_items('groups')
    groups.sort(key=lambda x: int(x.get('age_from', 0)) if x.get('age_from') and x['age_from'].isdigit() else 0)
    return render_template('requests/requests.html', items=pending_requests, groups=groups, section='Заявки')


@requests_bp.route('/approve/<child_id>', methods=['POST'])
@login_required
def approve(child_id):
    group_id = request.form.get('group_id')
    if not group_id:
        return redirect(url_for('requests.index'))

    children = get_children_with_parent()
    child = next((c for c in children if c['id'] == child_id), None)
    if not child or child.get('requestStatus') is not None:
        return redirect(url_for('requests.index'))

    update_child(child_id, {
        'requestStatus': True,
        'group_id': group_id,
    })

    set_child_group_id(child_id, group_id)

    old_group_id = child.get('group_id')
    if old_group_id and old_group_id != group_id:
        old_group = get_document('groups', old_group_id)
        if old_group:
            children_uids = old_group.get('children_uids', [])
            if child_id in children_uids:
                children_uids.remove(child_id)
            update_document('groups', old_group_id, {'children_uids': children_uids})

    group = get_document('groups', group_id)
    if group:
        children_uids = group.get('children_uids', []) or []
        if child_id not in children_uids:
            children_uids.append(child_id)
        update_document('groups', group_id, {'children_uids': children_uids})

    return redirect(url_for('requests.index'))


@requests_bp.route('/reject/<child_id>', methods=['POST'])
@login_required
def reject(child_id):
    child = get_document('children', child_id)
    if not child:
        return redirect(url_for('requests.index'))

    old_group_id = child.get('group_id')
    if old_group_id:
        old_group = get_document('groups', old_group_id)
        if old_group:
            children_uids = old_group.get('children_uids', []) or []
            if child_id in children_uids:
                children_uids.remove(child_id)
            update_document('groups', old_group_id, {'children_uids': children_uids})

    update_child(child_id, {
        'requestStatus': False,
        'group_id': None,
    })
    return redirect(url_for('requests.index'))


@requests_bp.route('/add', methods=['POST'])
@login_required
def add():
    parent_id = request.form.get('parent_id', '').strip()
    name = request.form.get('name', '').strip()
    birth_date = request.form.get('birth_date', '').strip()
    gender = request.form.get('gender', '').strip()
    health_text = request.form.get('health_text', '').strip()
    mood = request.form.get('mood', 'Отличное').strip()
    features = request.form.getlist('features')
    photo = request.files.get('photo')
    photo_url = _save_photo(photo) if photo else None
    if parent_id and name:
        child_data = {
            'name': name,
            'birthDate': birth_date,
            'gender': gender,
            'healthText': health_text,
            'mood': mood,
            'features': features,
            'inKindergarten': False,
            'requestStatus': None,
            'group_id': None,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'requestedAt': firestore.SERVER_TIMESTAMP,
        }
        if photo_url:
            child_data['photoUrl'] = photo_url
        create_child(parent_id, child_data)
    return redirect(url_for('requests.index'))
