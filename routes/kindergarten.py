from flask import Blueprint, redirect, request, url_for

from firebase_admin_service import get_document, set_document
from routes.auth import login_required
from template_utils import stream_template

kindergarten_bp = Blueprint('kindergarten', __name__, template_folder='../templates')


@kindergarten_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    info = get_document('kindergarten', 'info')
    if not info:
        info = {'id': 'info', 'name': '', 'phone': '', 'address': '', 'schedule': ''}

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        schedule = request.form.get('schedule', '').strip()
        set_document('kindergarten', 'info', {
            'name': name,
            'phone': phone,
            'address': address,
            'schedule': schedule,
        })
        return redirect(url_for('kindergarten.index'))

    return stream_template('kindergarten/kindergarten.html', info=info, section='Информация садика')
