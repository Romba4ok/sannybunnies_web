from flask import Blueprint, redirect, request, url_for
from template_utils import stream_template

from firebase_admin_service import (
    create_document,
    delete_document,
    get_children_with_parent,
    get_collection_items,
    get_document,
    get_users_by_role,
    remove_child_from_group,
    set_child_group_id,
    update_child,
    update_document,
)
from routes.auth import login_required

groups_bp = Blueprint('groups', __name__, template_folder='../templates')


def _get_children_candidates():
    return get_children_with_parent()


def _get_teachers_by_ids(teacher_ids):
    teachers = []
    for teacher_id in teacher_ids or []:
        teacher = get_document('users', teacher_id)
        if teacher:
            teachers.append(teacher)
    return teachers


def _get_children_by_ids(child_ids):
    children = []
    child_map = _build_child_map()
    for child_id in child_ids or []:
        child = child_map.get(child_id)
        if child:
            children.append(child)
    return children


def _build_child_map():
    return {child['id']: child for child in get_children_with_parent()}


def _assign_child_to_group(child, group_id):
    if not child:
        return
    child_id = child['id']
    old_group_id = child.get('group_id')
    if old_group_id and old_group_id != group_id:
        remove_child_from_group(old_group_id, child_id)
    set_child_group_id(child_id, group_id)
    update_child(child_id, {'group_id': group_id, 'requestStatus': True})


def _remove_child_from_group(child, group_id):
    if not child:
        return
    child_id = child['id']
    if child.get('group_id') == group_id:
        set_child_group_id(child_id, None)
    update_child(child_id, {'group_id': None, 'requestStatus': False})


@groups_bp.route('/')
@login_required
def index():
    items = get_collection_items('groups')
    items.sort(key=lambda x: int(x.get('age_from', 0)) if x.get('age_from') and x['age_from'].isdigit() else 0)
    return stream_template('groups/groups.html', items=items, section='Группы')


@groups_bp.route('/add_form')
@login_required
def add_form():
    teachers = get_users_by_role('teacher')
    children = _get_children_candidates()
    return stream_template('groups/add_group.html', teachers=teachers, children=children)


@groups_bp.route('/view/<group_id>')
@login_required
def view(group_id):
    group = get_document('groups', group_id)
    if not group:
        return redirect(url_for('groups.index'))

    group.setdefault('teacher_uids', [])
    group.setdefault('children_uids', [])
    teachers = _get_teachers_by_ids(group['teacher_uids'])
    children = _get_children_by_ids(group['children_uids'])
    return stream_template('groups/group_detail.html', group=group, teachers=teachers, children=children)


@groups_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name', 'Новая группа').strip()
    age_from = request.form.get('age_from', '').strip()
    age_to = request.form.get('age_to', '').strip()
    teacher_uids = request.form.getlist('teacher_uids') or request.form.getlist('teacher_uids[]')
    children_uids = request.form.getlist('children_uids') or request.form.getlist('children_uids[]')

    group_data = {
        'name': name,
        'age_from': age_from,
        'age_to': age_to,
        'teacher_uids': teacher_uids,
        'children_uids': children_uids,
    }

    group_id = create_document('groups', group_data)
    child_map = _build_child_map()
    for child_id in children_uids:
        _assign_child_to_group(child_map.get(child_id), group_id)
    return redirect(url_for('groups.index'))


@groups_bp.route('/edit/<group_id>', methods=['GET', 'POST'])
@login_required
def edit(group_id):
    group = get_document('groups', group_id)
    if not group:
        return redirect(url_for('groups.index'))

    if request.method == 'POST':
        name = request.form.get('name', 'Новая группа').strip()
        age_from = request.form.get('age_from', '').strip()
        age_to = request.form.get('age_to', '').strip()
        teacher_uids = request.form.getlist('teacher_uids') or request.form.getlist('teacher_uids[]')
        children_uids = request.form.getlist('children_uids') or request.form.getlist('children_uids[]')

        update_document('groups', group_id, {
            'name': name,
            'age_from': age_from,
            'age_to': age_to,
            'teacher_uids': teacher_uids,
            'children_uids': children_uids,
        })
        child_map = _build_child_map()
        old_children = group.get('children_uids', [])
        for child_id in children_uids:
            _assign_child_to_group(child_map.get(child_id), group_id)
        for child_id in old_children:
            if child_id not in children_uids:
                _remove_child_from_group(child_map.get(child_id), group_id)
        return redirect(url_for('groups.index'))

    teachers = get_users_by_role('teacher')
    children = _get_children_candidates()
    group.setdefault('teacher_uids', [])
    group.setdefault('children_uids', [])
    return stream_template('groups/edit_group.html', group=group, teachers=teachers, children=children)


@groups_bp.route('/delete/<group_id>', methods=['POST'])
@login_required
def delete(group_id):
    children = get_children_with_parent()
    for child in children:
        if child.get('group_id') == group_id:
            _remove_child_from_group(child, group_id)

    schedules = get_collection_items('schedule')
    for sched in schedules:
        if sched.get('group_id') == group_id:
            delete_document('schedule', sched['id'])

    menus = get_collection_items('menu')
    for menu in menus:
        if menu.get('group_id') == group_id:
            delete_document('menu', menu['id'])

    delete_document('groups', group_id)
    return redirect(url_for('groups.index'))
