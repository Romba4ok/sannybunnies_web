import requests
from requests.exceptions import ConnectionError, ProxyError, RequestException

from config import FIREBASE_API_KEY
from firebase_admin_service import get_document, query_user_by_email


class AuthError(Exception):
    pass


def _post_firebase_request(url: str, payload: dict) -> dict:
    try:
        session = requests.Session()
        session.trust_env = False
        response = session.post(url, json=payload, timeout=10)
        data = response.json()
    except ProxyError as exc:
        raise AuthError(
            'Сетевая ошибка: не удалось подключиться к Firebase. '
            'Проверьте настройки прокси или интернет-соединение.'
        ) from exc
    except ConnectionError as exc:
        raise AuthError(
            'Сетевая ошибка: не удалось подключиться к Firebase. '
            'Проверьте подключение к интернету.'
        ) from exc
    except RequestException as exc:
        raise AuthError(f'Ошибка сети при обращении к Firebase: {exc}') from exc
    except ValueError:
        raise AuthError('Не удалось разобрать ответ Firebase')

    return response, data


def sign_in_with_email_and_password(email: str, password: str) -> dict:
    if not FIREBASE_API_KEY:
        raise AuthError('FIREBASE_API_KEY не задан в config.py или .env')

    url = (
        f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}'
    )
    payload = {
        'email': email,
        'password': password,
        'returnSecureToken': True,
    }
    response, data = _post_firebase_request(url, payload)

    if response.status_code != 200 or 'error' in data:
        message = data.get('error', {}).get('message', 'Ошибка входа')
        raise AuthError(message)

    return data


def create_user_with_email_and_password(email: str, password: str) -> dict:
    if not FIREBASE_API_KEY:
        raise AuthError('FIREBASE_API_KEY не задан в config.py или .env')

    url = (
        f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}'
    )
    payload = {
        'email': email,
        'password': password,
        'returnSecureToken': True,
    }
    response, data = _post_firebase_request(url, payload)

    if response.status_code != 200 or 'error' in data:
        message = data.get('error', {}).get('message', 'Ошибка создания пользователя')
        raise AuthError(message)

    return data


def get_admin_profile(email: str, uid: str | None = None) -> dict | None:
    if uid:
        profile = get_document('users', uid)
        if profile:
            return profile
    return query_user_by_email(email)
