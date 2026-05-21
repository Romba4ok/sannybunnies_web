from flask import Blueprint, redirect, render_template, request, url_for
from itertools import zip_longest

from firebase_admin_service import (
    create_document,
    delete_document,
    get_collection_items,
    get_document,
    update_document,
    upload_photo_to_storage,
)
from routes.auth import login_required

menu_bp = Blueprint('menu', __name__, template_folder='../templates')

DAY_LABELS = {
    'monday': 'Понедельник',
    'tuesday': 'Вторник',
    'wednesday': 'Среда',
    'thursday': 'Четверг',
    'friday': 'Пятница',
    'saturday': 'Суббота',
    'sunday': 'Воскресенье',
}


def _save_photo(photo):
    if photo and getattr(photo, 'filename', None):
        return upload_photo_to_storage(photo, 'menu_photos')
    return None


def _parse_menu_rows(group_id, group_name):
    menu_rows = []
    for day in DAY_LABELS:
        times = request.form.getlist(f'{day}_time[]')
        meals = request.form.getlist(f'{day}_meal[]')
        kcals = request.form.getlist(f'{day}_kcal[]')
        descriptions = request.form.getlist(f'{day}_description[]')
        ingredients_list = request.form.getlist(f'{day}_ingredients[]')
        photos = request.files.getlist(f'{day}_photo[]')

        for index, (time, meal, kcal, description, ingredients_raw) in enumerate(
            zip(times, meals, kcals, descriptions, ingredients_list)
        ):
            photo = photos[index] if index < len(photos) else None
            if not (
                time.strip()
                or meal.strip()
                or kcal.strip()
                or description.strip()
                or ingredients_raw.strip()
                or (photo and getattr(photo, 'filename', None))
            ):
                continue
            ingredients = [line.strip() for line in ingredients_raw.splitlines() if line.strip()]
            menu_rows.append(
                {
                    'group_id': group_id,
                    'group_name': group_name,
                    'day': day,
                    'time': time.strip(),
                    'meal': meal.strip() or 'Блюдо',
                    'kcal': kcal.strip(),
                    'description': description.strip(),
                    'ingredients': ingredients,
                    'photo': photo,
                }
            )
    return menu_rows


@menu_bp.route('/')
@login_required
def index():
    items = get_collection_items('menu')
    for item in items:
        if item.get('day') not in DAY_LABELS:
            item['day'] = 'monday'
    items.sort(
        key=lambda item: (
            item.get('group_name') or '',
            list(DAY_LABELS.keys()).index(item.get('day', 'monday')),
            item.get('meal') or '',
        )
    )
    items_by_group = {}
    for item in items:
        group_key = item.get('group_name') or item.get('group_id') or 'Без группы'
        if group_key not in items_by_group:
            items_by_group[group_key] = {'group_id': item.get('group_id'), 'days': {day: [] for day in DAY_LABELS}}
        items_by_group[group_key]['days'][item['day']].append(item)
    return render_template('menu/menu.html', items_by_group=items_by_group, day_labels=DAY_LABELS, section='Меню питания')


@menu_bp.route('/add_form')
@login_required
def add_form():
    groups = get_collection_items('groups')
    groups.sort(key=lambda group: group.get('name') or group.get('id') or '')
    selected_group_id = request.args.get('group_id')
    return render_template(
        'menu/add_menu.html',
        groups=groups,
        selected_group_id=selected_group_id,
        day_labels=DAY_LABELS,
        section='Меню питания',
    )


@menu_bp.route('/group/<group_id>')
@login_required
def group_menu(group_id):
    group = get_document('groups', group_id)
    if not group:
        return redirect(url_for('menu.index'))

    items = get_collection_items('menu')
    group_items = [item for item in items if item.get('group_id') == group_id]
    group_items.sort(key=lambda item: (list(DAY_LABELS.keys()).index(item.get('day', 'monday')), item.get('meal') or ''))

    items_by_day = {day: [] for day in DAY_LABELS}
    for item in group_items:
        items_by_day[item.get('day', 'monday')].append(item)

    return render_template(
        'menu/group_menu.html',
        group=group,
        items_by_day=items_by_day,
        day_labels=DAY_LABELS,
        section='Меню питания',
    )


@menu_bp.route('/add', methods=['POST'])
@login_required
def add():
    group_id = request.form.get('group_id')
    group = get_document('groups', group_id) if group_id else None
    if not group:
        return redirect(url_for('menu.index'))

    menu_rows = _parse_menu_rows(group_id, group.get('name') or '')
    for row in menu_rows:
        photo_url = _save_photo(row.pop('photo'))
        row['photo_url'] = photo_url
        create_document('menu', row)
    return redirect(url_for('menu.index'))


@menu_bp.route('/edit/<menu_id>', methods=['GET', 'POST'])
@login_required
def edit(menu_id):
    menu_item = get_document('menu', menu_id)
    if not menu_item:
        return redirect(url_for('menu.index'))

    groups = get_collection_items('groups')
    groups.sort(key=lambda group: group.get('name') or group.get('id') or '')

    if request.method == 'POST':
        group_id = request.form.get('group_id')
        group = get_document('groups', group_id) if group_id else None
        if not group:
            return redirect(url_for('menu.index'))

        day = request.form.get('day', 'monday')
        if day not in DAY_LABELS:
            day = 'monday'
        time = request.form.get('time', '').strip()
        meal = request.form.get('meal', 'Новое блюдо').strip()
        kcal = request.form.get('kcal', '').strip()
        description = request.form.get('description', '').strip()
        ingredients_raw = request.form.get('ingredients', '').strip()
        ingredients = [line.strip() for line in ingredients_raw.splitlines() if line.strip()]
        photo = request.files.get('photo')
        photo_url = menu_item.get('photo_url')
        new_photo_url = _save_photo(photo)
        if new_photo_url:
            photo_url = new_photo_url

        update_document('menu', menu_id, {
            'group_id': group_id,
            'group_name': group.get('name') or '',
            'day': day,
            'time': time,
            'meal': meal,
            'kcal': kcal,
            'description': description,
            'ingredients': ingredients,
            'photo_url': photo_url,
        })
        return redirect(url_for('menu.index'))

    return render_template('menu/edit_menu.html', menu=menu_item, groups=groups, day_labels=DAY_LABELS, section='Меню питания')


@menu_bp.route('/delete/<menu_id>', methods=['POST'])
@login_required
def delete(menu_id):
    delete_document('menu', menu_id)
    return redirect(url_for('menu.index'))


@menu_bp.route('/delete_group/<group_id>', methods=['POST'])
@login_required
def delete_group_menu(group_id):
    items = get_collection_items('menu')
    for item in items:
        if item.get('group_id') == group_id:
            delete_document('menu', item['id'])
    return redirect(url_for('menu.index'))
