from flask import Flask, redirect, url_for, send_from_directory
from config import SECRET_KEY, UPLOAD_FOLDER
from firebase_admin_service import init_firebase
from routes.auth import auth_bp
from routes.faq import faq_bp
from routes.groups import groups_bp
from routes.interior import interior_bp
from routes.kindergarten import kindergarten_bp
from routes.menu import menu_bp
from routes.news import news_bp
from routes.requests import requests_bp
from routes.reviews import reviews_bp
from routes.schedule import schedule_bp
from routes.teachers import teachers_bp
from routes.users import users_bp


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = SECRET_KEY

    init_firebase()

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(requests_bp, url_prefix='/requests')
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
    app.register_blueprint(groups_bp, url_prefix='/groups')
    app.register_blueprint(teachers_bp, url_prefix='/teachers')
    app.register_blueprint(reviews_bp, url_prefix='/reviews')
    app.register_blueprint(news_bp, url_prefix='/news')
    app.register_blueprint(interior_bp, url_prefix='/interior')
    app.register_blueprint(menu_bp, url_prefix='/menu')
    app.register_blueprint(kindergarten_bp, url_prefix='/kindergarten')
    app.register_blueprint(faq_bp, url_prefix='/faq')

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
