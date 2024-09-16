import logging
import re
import secrets
import string
from typing import Optional

from sleutelkastje.application import db
from sleutelkastje.management import Key
from sleutelkastje.sysop import Application


letters = string.ascii_letters
digits = string.digits
special_chars = re.sub(r'["\'\\!]', '', string.punctuation)
alphabet = letters + digits + special_chars


def is_func(app, eppn):
    # cur.execute("SELECT funcPerson FROM application WHERE mnemonic = %s", [app])
    application = db.session.query(Application).filter_by(mnemonic=app).first()
    functional_admin = application.functional_admin
    if functional_admin is None:
        return False
    logging.debug(f'fp: {functional_admin.username} ({eppn == functional_admin.username})')
    return eppn == functional_admin.username


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
