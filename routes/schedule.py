from flask import Blueprint, redirect, request, url_for
from template_utils import stream_template

from firebase_admin_service import (
    create_document,
    delete_document,
    get_collection_items,
    get_document,
    iter_collection_items,
    update_document,
)
from routes.auth import login_required

schedule_bp = Blueprint('schedule', __name__, template_folder='../templates')

DAY_LABELS = {
    'monday': 'Понедельник',
    'tuesday': 'Вторник',
    'wednesday': 'Среда',
    'thursday': 'Четверг',
    'friday': 'Пятница',
    'saturday': 'Суббота',
    'sunday': 'Воскресенье',
}


def _build_week_from_form():
    days = {}
    for day in DAY_LABELS:
        times = request.form.getlist(f'{day}_time[]')
        titles = request.form.getlist(f'{day}_title[]')
        items = []
        for time, title in zip(times, titles):
            time = time.strip()
            title = title.strip()
            if title or time:
                items.append({'time': time, 'title': title})
        days[day] = items
    return days


@schedule_bp.route('/')
@login_required
def index():
    items = iter_collection_items('schedule')
    return stream_template('schedule/schedule.html', items=items, section='Расписание')


@schedule_bp.route('/add_form')
@login_required
def add_form():
    groups = get_collection_items('groups')
    groups.sort(key=lambda x: int(x.get('age_from', 0)) if x.get('age_from') and x['age_from'].isdigit() else 0)
    return stream_template('schedule/add_schedule.html', groups=groups, section='Расписание')


@schedule_bp.route('/add', methods=['POST'])
@login_required
def add():
    group_id = request.form.get('group_id')
    group = get_document('groups', group_id) if group_id else None
    if not group:
        return redirect(url_for('schedule.index'))
    days = _build_week_from_form()
    schedule_data = {
        'group_id': group_id,
        'group_name': group.get('name') or '',
        'days': days,
    }
    create_document('schedule', schedule_data)
    return redirect(url_for('schedule.index'))


@schedule_bp.route('/edit/<schedule_id>', methods=['GET', 'POST'])
@login_required
def edit(schedule_id):
    schedule = get_document('schedule', schedule_id)
    if not schedule:
        return redirect(url_for('schedule.index'))
    groups = get_collection_items('groups')
    groups.sort(key=lambda x: int(x.get('age_from', 0)) if x.get('age_from') and x['age_from'].isdigit() else 0)
    if request.method == 'POST':
        group_id = request.form.get('group_id')
        group = get_document('groups', group_id) if group_id else None
        if not group:
            return redirect(url_for('schedule.index'))
        days = _build_week_from_form()
        update_document('schedule', schedule_id, {
            'group_id': group_id,
            'group_name': group.get('name') or '',
            'days': days,
        })
        return redirect(url_for('schedule.index'))

    schedule.setdefault('days', {})
    return stream_template('schedule/edit_schedule.html', schedule=schedule, groups=groups, section='Расписание')


@schedule_bp.route('/delete/<schedule_id>', methods=['POST'])
@login_required
def delete(schedule_id):
    delete_document('schedule', schedule_id)
    return redirect(url_for('schedule.index'))
