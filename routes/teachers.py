from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from firebase_admin_service import (
    create_teacher_user,
    get_users_by_role,
    update_teacher,
    delete_teacher,
    get_document,
    update_user_password,
    upload_photo_to_storage,
)
from routes.auth import login_required

teachers_bp = Blueprint('teachers', __name__, template_folder='../templates')


@teachers_bp.route('/add_form')
@login_required
def add_form():
    return render_template('teachers/add_teacher.html')


@teachers_bp.route('/')
@login_required
def index():
    teachers = get_users_by_role('teacher')
    return render_template('teachers/teachers.html', teachers=teachers, section='Воспитатели')


@teachers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        name = request.form.get('name', '').strip()
        position = request.form.get('position', '').strip()
        description = request.form.get('description', '').strip()

        photo_url = None
        file = request.files.get('photo')
        if file and getattr(file, 'filename', None):
            photo_url = upload_photo_to_storage(file, 'teacher_photos')

        if not all([email, password, name]):
            flash('Email, пароль и имя обязательны', 'error')
            return render_template('teachers/add_teacher.html')

        try:
            create_teacher_user(email, password, name, position, description, photo_url)
            flash('Воспитатель успешно создан', 'success')
            return redirect(url_for('teachers.index'))
        except Exception as e:
            flash(f'Ошибка при создании: {str(e)}', 'error')

    return render_template('teachers/add_teacher.html')


@teachers_bp.route('/edit/<teacher_id>', methods=['GET'])
@login_required
def edit_form(teacher_id):
    teacher = get_document('users', teacher_id)
    if not teacher or teacher.get('role') != 'teacher':
        flash('Воспитатель не найден', 'error')
        return redirect(url_for('teachers.index'))
    return render_template('teachers/edit_teacher.html', teacher=teacher)


@teachers_bp.route('/edit/<teacher_id>', methods=['POST'])
@login_required
def edit(teacher_id):
    teacher = get_document('users', teacher_id)
    if not teacher or teacher.get('role') != 'teacher':
        flash('Воспитатель не найден', 'error')
        return redirect(url_for('teachers.index'))

    name = request.form.get('name', '').strip()
    position = request.form.get('position', '').strip()
    description = request.form.get('description', '').strip()
    password = request.form.get('password', '').strip()

    photo_url = teacher.get('photo_url')
    file = request.files.get('photo')
    if file and getattr(file, 'filename', None):
        new_photo_url = upload_photo_to_storage(file, 'teacher_photos')
        if new_photo_url:
            photo_url = new_photo_url

    try:
        if password:
            update_user_password(teacher.get('uid'), password)
        update_teacher(teacher_id, name, position, description, photo_url)
        flash('Воспитатель успешно обновлён', 'success')
        return redirect(url_for('teachers.index'))
    except Exception as e:
        flash(f'Ошибка при обновлении: {str(e)}', 'error')
    return render_template('teachers/edit_teacher.html', teacher=teacher)


@teachers_bp.route('/delete/<teacher_id>', methods=['POST'])
@login_required
def delete(teacher_id):
    try:
        delete_teacher(teacher_id)
        flash('Воспитатель успешно удалён', 'success')
    except Exception as e:
        flash(f'Ошибка при удалении: {str(e)}', 'error')
    return redirect(url_for('teachers.index'))
