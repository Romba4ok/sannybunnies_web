from flask import Blueprint, redirect, request, url_for
from template_utils import stream_template
from firebase_admin import firestore

from firebase_admin_service import create_document, delete_document, get_document, update_document, upload_photo_to_storage, get_firestore, normalize_document
from routes.auth import login_required

news_bp = Blueprint('news', __name__, template_folder='../templates')


@news_bp.route('/')
@login_required
def index():
    db = get_firestore()
    docs = db.collection('news').order_by('createdAt', direction=firestore.Query.DESCENDING).stream()
    items = (normalize_document(doc) for doc in docs)
    return stream_template('news/news.html', items=items, section='Новости')


@news_bp.route('/add_form')
@login_required
def add_form():
    return stream_template('news/add_news.html', section='Новости')


@news_bp.route('/add', methods=['POST'])
@login_required
def add():
    headline = request.form.get('headline', 'Новость').strip()
    body = request.form.get('body', '').strip()
    photo = request.files.get('photo')
    photo_url = None
    if photo and photo.filename:
        photo_url = upload_photo_to_storage(photo, 'news_photos')
    create_document('news', {'headline': headline, 'body': body, 'photo_url': photo_url, 'createdAt': firestore.SERVER_TIMESTAMP})
    return redirect(url_for('news.index'))


@news_bp.route('/edit/<news_id>', methods=['GET', 'POST'])
@login_required
def edit(news_id):
    news_item = get_document('news', news_id)
    if not news_item:
        return redirect(url_for('news.index'))
    if request.method == 'POST':
        headline = request.form.get('headline', 'Новость').strip()
        body = request.form.get('body', '').strip()
        photo = request.files.get('photo')
        photo_url = news_item.get('photo_url')
        if photo and photo.filename:
            new_photo_url = upload_photo_to_storage(photo, 'news_photos')
            if new_photo_url:
                photo_url = new_photo_url
        update_document('news', news_id, {'headline': headline, 'body': body, 'photo_url': photo_url})
        return redirect(url_for('news.index'))

    return stream_template('news/edit_news.html', news=news_item, section='Новости')


@news_bp.route('/delete/<news_id>', methods=['POST'])
@login_required
def delete(news_id):
    delete_document('news', news_id)
    return redirect(url_for('news.index'))
