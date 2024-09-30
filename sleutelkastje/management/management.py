import re
import secrets
import string
from typing import Optional

from sleutelkastje.application import db
from sleutelkastje.authentication import Key
from sleutelkastje.sysop import Application, ApplicationUserAssociation

letters = string.ascii_letters
digits = string.digits
special_chars = re.sub(r'["\'\\!]', '', string.punctuation)
alphabet = letters + digits + special_chars


def is_func(app: str, user_id: int) -> bool:
    application = db.session.query(Application).filter_by(mnemonic=app).first()
    application_association = (db.session.query(ApplicationUserAssociation)
                               .filter_by(app_id=application.id, user_id=user_id)).one_or_none()

    if application_association is None:
        return False

    return application_association.role == 'operator'


def get_invite(length=48):
    key = ''
    for i in range(length):
        key += ''.join(secrets.choice(letters + digits))
    return key


def key_valid(key: str, app_name: str) -> tuple[Optional[Key], bool]:
    """
    Validate if given key is valid for the application.
    :param key:
    :param app_name:
    :return:
    """
    key_obj = db.session.query(Key).filter_by(key=key).first()

    if key_obj is None:
        return key_obj, False

    valid = False
    for invitation in key_obj.user.invitations:
        if invitation.application.mnemonic == app_name:
            valid = True
            break
    return key_obj, valid
