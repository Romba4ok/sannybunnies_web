import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'replace-this-secret')
FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', 'serviceAccountKey.json')
FIREBASE_API_KEY = os.getenv('FIREBASE_API_KEY', 'AIzaSyBvRRv_3MmDaPuRfolhB1HIrqK44hvsdoU')
FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN', 'sunnybunnies.firebaseapp.com')
FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID', 'sunnybunnies')
FIREBASE_STORAGE_BUCKET = os.getenv('FIREBASE_STORAGE_BUCKET', 'sunnybunnies.firebasestorage.app')
FIREBASE_MESSAGING_SENDER_ID = os.getenv('FIREBASE_MESSAGING_SENDER_ID', '1057663994055')
FIREBASE_APP_ID = os.getenv('FIREBASE_APP_ID', '1:1057663994055:web:88e739871013f92b2b56e2')
FIREBASE_MEASUREMENT_ID = os.getenv('FIREBASE_MEASUREMENT_ID', 'G-RPD1QDMYHW')
ADMIN_ROLE = os.getenv('ADMIN_ROLE', 'admin')


UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

FIREBASE_CONFIG = {
'apiKey': FIREBASE_API_KEY,
'authDomain': FIREBASE_AUTH_DOMAIN,
'projectId': FIREBASE_PROJECT_ID,
'storageBucket': FIREBASE_STORAGE_BUCKET,
'messagingSenderId': FIREBASE_MESSAGING_SENDER_ID,
'appId': FIREBASE_APP_ID,
'measurementId': FIREBASE_MEASUREMENT_ID,
}



















