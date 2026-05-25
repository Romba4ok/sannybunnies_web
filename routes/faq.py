from flask import Blueprint, redirect, request, url_for

from firebase_admin_service import create_document, delete_document, get_document, iter_collection_items, update_document
from routes.auth import login_required
from template_utils import stream_template

faq_bp = Blueprint('faq', __name__, template_folder='../templates')


@faq_bp.route('/')
@login_required
def index():
    items = list(iter_collection_items('faq'))
    return stream_template('faq/faq.html', items=items, section='Часто задаваемые вопросы')


@faq_bp.route('/add_form')
@login_required
def add_form():
    return stream_template('faq/add_faq.html', section='Часто задаваемые вопросы')


@faq_bp.route('/add', methods=['POST'])
@login_required
def add():
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    create_document('faq', {'question': question, 'answer': answer})
    return redirect(url_for('faq.index'))


@faq_bp.route('/edit/<faq_id>', methods=['GET', 'POST'])
@login_required
def edit(faq_id):
    faq_item = get_document('faq', faq_id)
    if not faq_item:
        return redirect(url_for('faq.index'))
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        update_document('faq', faq_id, {'question': question, 'answer': answer})
        return redirect(url_for('faq.index'))

    return stream_template('faq/edit_faq.html', faq=faq_item)


@faq_bp.route('/delete/<faq_id>', methods=['POST'])
@login_required
def delete(faq_id):
    delete_document('faq', faq_id)
    return redirect(url_for('faq.index'))
