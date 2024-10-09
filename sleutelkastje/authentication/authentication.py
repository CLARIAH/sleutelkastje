import os
import string
import re
import secrets
from datetime import datetime
from sys import platform

from flask_login import LoginManager

from sleutelkastje import app

from flask_httpauth import HTTPBasicAuth
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata

from werkzeug.security import generate_password_hash, check_password_hash

from sleutelkastje.application import db
from sleutelkastje.authentication import Key, User
from sleutelkastje.database import users


login_manager = LoginManager()
login_manager.init_app(app)

auth = HTTPBasicAuth()

oidc_auth = OIDCAuthentication({'default': ProviderConfiguration(
    issuer=os.environ['OIDC_SERVER'],
    client_metadata=ClientMetadata(
        client_id=os.environ['OIDC_CLIENT_ID'],
        client_secret=os.environ['OIDC_CLIENT_SECRET']),
    auth_request_params={'scope': ['openid', 'email', 'profile'],
                         'claims': {"userinfo": {"edupersontargetedid": None, "schac_home_organisation": None,
                                                 "nickname": None, "email": None, "eppn": None, "idp": None}}})},
    app) if 'OIDC_SERVER' in os.environ and len(os.environ['OIDC_SERVER']) > 0 else None


@login_manager.user_loader
def load_user(user_id: str) -> User:
    """
    Load user by ID.
    :param user_id:
    :return:
    """
    return db.session.query(User).filter(User.username == user_id).one_or_none()


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key and api_key != '':
        if not api_key.startswith('Bearer huc:'):
            return None
        api_key = api_key.replace('Bearer ', '', 1)
        user = get_user_by_key(api_key)
        return user

    return None


@auth.verify_password
def verify_password(username, password):
    user = load_user(username)
    if user is not None and check_password_hash(user.password_hash, password):
        return user


@auth.get_user_roles
def get_user_roles(user):
    return user.role


def get_user_by_key(api_key: str):
    prefix = api_key[4:20]

    key = db.session.query(Key).filter(Key.key_prefix == prefix).one_or_none()
    if key is not None and check_password_hash(key.key_hash, api_key):
        key.last_used = datetime.now()
        db.session.commit()
        return key.user
    return None


letters = string.ascii_letters
digits = string.digits
special_chars = re.sub(r'["\'\\!]', '', string.punctuation)
alphabet = letters + digits + special_chars


def hash_password(password):
    """
    Generate a password hash
    :param password:
    :return:
    """
    if platform == "linux" or platform == "linux2":
        return generate_password_hash(password)
    else:
        # The default method (scrypt) requires OpenSSL, not present on Mac
        return generate_password_hash(password, method='pbkdf2')


def generate_random_string(length):
    return ''.join([secrets.choice(alphabet) for i in range(length)])


def get_api_key(length=48):
    """
    Returns both the key and the prefix
    :param length:
    :return:
    """
    prefix = generate_random_string(16)
    key = generate_random_string(length)
    return prefix, f'huc:{prefix}{key}'


users['sysop'] = {
    "password": hash_password("striktgeheim"),
    "role": "sysop",
}
