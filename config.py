import os
from dotenv import load_dotenv

load_dotenv()

os.environ.pop('FIRESTORE_EMULATOR_HOST', None)
os.environ.pop('FIREBASE_AUTH_EMULATOR_HOST', None)
os.environ.pop('FIREBASE_DATABASE_EMULATOR_HOST', None)
for proxy_var in (
    'HTTP_PROXY',
    'HTTPS_PROXY',
    'ALL_PROXY',
    'http_proxy',
    'https_proxy',
    'all_proxy',
):
    os.environ.pop(proxy_var, None)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-change-in-production')
FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', 'serviceAccountKey.json')
if not os.path.isabs(FIREBASE_CREDENTIALS):
    FIREBASE_CREDENTIALS = os.path.join(BASE_DIR, FIREBASE_CREDENTIALS)
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID')
FIREBASE_MEASUREMENT_ID = os.getenv('FIREBASE_MEASUREMENT_ID')
ADMIN_ROLE = os.getenv('ADMIN_ROLE', 'admin')


UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

FIREBASE_CONFIG = {
'apiKey': FIREBASE_API_KEY,
'authDomain': FIREBASE_AUTH_DOMAIN,
'projectId': FIREBASE_PROJECT_ID,
'storageBucket': FIREBASE_STORAGE_BUCKET,
'messagingSenderId': FIREBASE_MESSAGING_SENDER_ID,
'appId': FIREBASE_APP_ID,
'measurementId': FIREBASE_MEASUREMENT_ID,
}



















