import os

# ХАК: Принудительно очищаем переменные эмулятора перед инициализацией,
# чтобы Firestore SDK не пытался подключаться к локальному порту 9.
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

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, auth, storage
from google.api_core.retry import Retry
from google.cloud import firestore_v1
from datetime import datetime

from config import FIREBASE_CREDENTIALS, FIREBASE_STORAGE_BUCKET

FIRESTORE_TIMEOUT = 8
FIRESTORE_RETRY = Retry(deadline=FIRESTORE_TIMEOUT)

firebase_app = None


def init_firebase():
    global firebase_app
    if firebase_app is None:
        if not os.path.exists(FIREBASE_CREDENTIALS):
            raise FileNotFoundError(
                f"Firebase credentials not found: {FIREBASE_CREDENTIALS}. "
                "Скопируй сервисный файл JSON и укажи путь в переменной FIREBASE_CREDENTIALS"
            )
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        
        # ИСПРАВЛЕНИЕ: Передаем имя бакета при инициализации, чтобы работал Storage
        firebase_app = initialize_app(cred, {
            'storageBucket': FIREBASE_STORAGE_BUCKET
        })
    return firebase_app


def get_firestore():
    init_firebase()
    return firestore.client()


def normalize_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def normalize_document(doc):
    data = doc.to_dict() if doc is not None else {}
    normalized = {}
    for key, value in (data or {}).items():
        if hasattr(value, 'isoformat'):
            normalized[key] = value.isoformat()
        else:
            normalized[key] = value
    normalized['id'] = doc.id if doc is not None else None
    return normalized


def get_collection_items(collection_name):
    db = get_firestore()
    docs = db.collection(collection_name).stream(retry=FIRESTORE_RETRY, timeout=FIRESTORE_TIMEOUT)
    return [normalize_document(doc) for doc in docs]


def get_users_by_role(role):
    users = get_collection_items('users')
    if role == 'parent':
        return [u for u in users if u.get('role') in ['parent', 'user']]
    return [u for u in users if u.get('role') == role]


def get_children_with_parent():
    db = get_firestore()
    children = []
    docs = db.collection('children').stream(retry=FIRESTORE_RETRY, timeout=FIRESTORE_TIMEOUT)
    for doc in docs:
        child = normalize_document(doc)

        parent_id = child.get('parent_id') or child.get('parent_uid')
        parent_data = {}
        if parent_id:
            parent_doc = db.collection('users').document(parent_id).get(retry=FIRESTORE_RETRY, timeout=FIRESTORE_TIMEOUT)
            if parent_doc.exists:
                parent_data = parent_doc.to_dict() or {}

        parent_name = parent_data.get('name') or parent_data.get('email') or parent_id
        child['parent_name'] = parent_name
        child['parent_id'] = parent_id
        child['parent_phone'] = parent_data.get('phone') or parent_data.get('phoneNumber')
        child['parent_photo'] = parent_data.get('photoUrl') or parent_data.get('photo_url')
        child['parent_email'] = parent_data.get('email')

        if child.get('group_id'):
            group_doc = db.collection('groups').document(child['group_id']).get(retry=FIRESTORE_RETRY, timeout=FIRESTORE_TIMEOUT)
            group_data = group_doc.to_dict() if group_doc and group_doc.exists else {}
            child['group_name'] = group_data.get('name')

        if not child.get('name'):
            child['name'] = child.get('child_name') or child.get('first_name') or child.get('last_name') or child.get('email')

        children.append(child)
    return children


def get_document(collection_name, doc_id):
    db = get_firestore()
    doc = db.collection(collection_name).document(doc_id).get(retry=FIRESTORE_RETRY, timeout=FIRESTORE_TIMEOUT)
    return normalize_document(doc) if doc and doc.exists else None


def set_child_group_id(*args):
    if len(args) == 1:
        child_id = args[0]
        group_id = None
    elif len(args) == 2:
        child_id, group_id = args
    elif len(args) == 3:
        _, child_id, group_id = args
    else:
        raise TypeError("set_child_group_id accepts 1..3 positional arguments")

    db = get_firestore()
    child_ref = db.collection('children').document(child_id)
    child_doc = child_ref.get(retry=FIRESTORE_RETRY, timeout=FIRESTORE_TIMEOUT)
    if not child_doc or not child_doc.exists:
        return
    if group_id is None:
        child_ref.update({'group_id': firestore.DELETE_FIELD})
    else:
        child_ref.update({'group_id': group_id})


def update_child(child_id, data):
    db = get_firestore()
    child_ref = db.collection('children').document(child_id)
    child_doc = child_ref.get(retry=FIRESTORE_RETRY, timeout=FIRESTORE_TIMEOUT)
    if not child_doc or not child_doc.exists:
        return
    child_ref.update(data)


def create_document(collection_name, data):
    db = get_firestore()
    doc_ref = db.collection(collection_name).document()
    doc_ref.set(data)
    return doc_ref.id


def update_document(collection_name, doc_id, data):
    db = get_firestore()
    db.collection(collection_name).document(doc_id).update(data)


def update_user_password(uid, password):
    init_firebase()
    auth.update_user(uid, password=password)


def set_document(collection_name, doc_id, data):
    db = get_firestore()
    db.collection(collection_name).document(doc_id).set(data)


def delete_document(collection_name, doc_id):
    db = get_firestore()
    db.collection(collection_name).document(doc_id).delete()


def query_user_by_email(email):
    db = get_firestore()
    query = db.collection('users').where(filter=firestore_v1.FieldFilter('email', '==', email)).limit(1).stream(retry=FIRESTORE_RETRY, timeout=FIRESTORE_TIMEOUT)
    for doc in query:
        return normalize_document(doc)
    return None


def create_teacher_user(email, password, name, position, description, photo_url=None):
    init_firebase()
    user = auth.create_user(email=email, password=password, display_name=name)
    user_data = {
        'uid': user.uid,
        'name': name,
        'email': email,
        'role': 'teacher',
        'position': position,
        'description': description,
        'createdAt': firestore.SERVER_TIMESTAMP,
    }
    if photo_url:
        user_data['photo_url'] = photo_url
    set_document('users', user.uid, user_data)
    return user.uid


def update_teacher(doc_id, name, position, description, photo_url=None):
    update_data = {
        'name': name,
        'position': position,
        'description': description,
    }
    if photo_url:
        update_data['photo_url'] = photo_url
    update_document('users', doc_id, update_data)


def delete_teacher(doc_id):
    init_firebase()
    user_doc = get_document('users', doc_id)
    if user_doc:
        try:
            auth.delete_user(user_doc['uid'])
        except Exception:
            pass
    delete_document('users', doc_id)


def create_child(parent_id, child_data):
    db = get_firestore()
    child_data = dict(child_data or {})
    child_data['parent_id'] = parent_id
    child_data['parent_uid'] = parent_id
    doc_ref = db.collection('children').document()
    doc_ref.set(child_data)
    return doc_ref.id


def remove_child_from_group(group_id, child_id):
    group = get_document('groups', group_id)
    if group:
        children_uids = group.get('children_uids', [])
        if child_id in children_uids:
            children_uids.remove(child_id)
        update_document('groups', group_id, {'children_uids': children_uids})


def upload_photo_to_storage(file, folder_path):
    if not file or not getattr(file, 'filename', None):
        return None
    try:
        init_firebase()
        # Метод bucket() теперь автоматически подхватит имя из initialize_app
        bucket = storage.bucket()
        blob_name = f"{folder_path}/{file.filename}"
        blob = bucket.blob(blob_name)
        
        # Сбрасываем указатель файла в начало на случай, если его читали ранее
        if hasattr(file, 'seek'):
            file.seek(0)
            
        blob.upload_from_string(file.read(), content_type=getattr(file, 'content_type', None))
        try:
            blob.make_public()
            return blob.public_url
        except Exception as pe:
            print(f"Warning: Could not make blob public, returning default URL: {pe}")
            return blob.public_url
    except Exception as e:
        print(f"Error uploading file to Firebase Storage: {e}")
    return None
