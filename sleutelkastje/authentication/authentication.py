import os
import string
import re
import secrets
from sys import platform

from sleutelkastje import app

from flask_httpauth import HTTPBasicAuth
from flask_pyoidc import OIDCAuthentication
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata

from werkzeug.security import generate_password_hash, check_password_hash

from sleutelkastje.database import users

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


@auth.verify_password
def verify_password(username, password):
    if username in users and \
            check_password_hash(users.get(username)["password"], password):
        return username


@auth.get_user_roles
def get_user_roles(user):
    return users[user]['role']


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


def get_api_key(length=48):
    key = ''
    for i in range(length):
        key += ''.join(secrets.choice(alphabet))
    return f'huc:{key}'


users['sysop'] = {
    "password": hash_password("striktgeheim"),
    "role": "sysop",
}
