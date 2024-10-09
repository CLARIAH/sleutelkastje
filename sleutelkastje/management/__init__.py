"""
This module is responsible for managing users from the application side. Invite users, accept
invitations and validate API keys.
"""

from flask import Blueprint

bp = Blueprint(
    'management',
    __name__,
    template_folder='templates',
    url_prefix='/api/apps'
)

from sleutelkastje.management.models import *
from sleutelkastje.management.management import is_func, get_invite, key_valid
from sleutelkastje.management import routes
