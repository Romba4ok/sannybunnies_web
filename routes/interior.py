from flask import Blueprint, redirect, render_template, request, url_for

from config import UPLOAD_FOLDER
from firebase_admin_service import (
    create_document,
    delete_document,
    get_collection_items,
    get_document,
    update_document,
    upload_photo_to_storage,
)
from routes.auth import login_required

interior_bp = Blueprint('interior', __name__, template_folder='../templates')


def _save_photo(photo):
    if photo and getattr(photo, 'filename', None):
        return upload_photo_to_storage(photo, 'interior_photos')
    return None


@interior_bp.route('/')
@login_required
def index():
    items = get_collection_items('interior')
    return render_template('interior/interior.html', items=items, section='Интерьер')


@interior_bp.route('/add_form')
@login_required
def add_form():
    return render_template('interior/add_interior.html', section='Интерьер')


@interior_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name', '').strip()
    if not name:
        return redirect(url_for('interior.index'))

    photos = []
    descriptions = request.form.getlist('description[]')
    photo_files = request.files.getlist('photo[]')
    for desc, photo in zip(descriptions, photo_files):
        photo_url = _save_photo(photo)
        if photo_url or desc.strip():
            photos.append({'url': photo_url, 'description': desc.strip()})

    if photos:
        create_document('interior', {
            'name': name,
            'photos': photos,
        })
    return redirect(url_for('interior.index'))


@interior_bp.route('/edit/<interior_id>', methods=['GET', 'POST'])
@login_required
def edit(interior_id):
    interior = get_document('interior', interior_id)
    if not interior:
        return redirect(url_for('interior.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            return redirect(url_for('interior.index'))

        photos = []
        descriptions = request.form.getlist('description[]')
        photo_files = request.files.getlist('photo[]')
        existing_photos = interior.get('photos', [])
        for i, (desc, photo) in enumerate(zip(descriptions, photo_files)):
            photo_url = _save_photo(photo)
            if photo_url or desc.strip():
                photos.append({'url': photo_url or (existing_photos[i]['url'] if i < len(existing_photos) else None), 'description': desc.strip()})

        update_document('interior', interior_id, {
            'name': name,
            'photos': photos,
        })
        return redirect(url_for('interior.index'))

    return render_template('interior/edit_interior.html', interior=interior, section='Интерьер')


@interior_bp.route('/delete/<interior_id>', methods=['POST'])
@login_required
def delete(interior_id):
    delete_document('interior', interior_id)
    return redirect(url_for('interior.index'))
