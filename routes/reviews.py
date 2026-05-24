from flask import Blueprint, redirect, request, url_for
from template_utils import stream_template

from firebase_admin_service import get_document, iter_collection_items, update_document, delete_document
from routes.auth import login_required

reviews_bp = Blueprint('reviews', __name__, template_folder='../templates')


@reviews_bp.route('/')
@login_required
def index():
    items = iter_collection_items('reviews')
    return stream_template('reviews/reviews.html', items=items, section='Отзывы')


@reviews_bp.route('/edit/<review_id>', methods=['GET', 'POST'])
@login_required
def edit(review_id):
    review = get_document('reviews', review_id)
    if not review:
        return redirect(url_for('reviews.index'))

    if request.method == 'POST':
        rating = request.form.get('rating', '5').strip()
        text = request.form.get('text', '').strip()
        update_document('reviews', review_id, {'rating': float(rating), 'text': text})
        return redirect(url_for('reviews.index'))

    return stream_template('reviews/edit_review.html', review=review)


@reviews_bp.route('/delete/<review_id>', methods=['POST'])
@login_required
def delete(review_id):
    delete_document('reviews', review_id)
    return redirect(url_for('reviews.index'))
