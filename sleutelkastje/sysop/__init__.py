from flask import Blueprint

bp = Blueprint(
    'sysop',
    __name__,
    url_prefix='/api/admin',
    template_folder='templates',
)

from sleutelkastje.sysop.models import *
from sleutelkastje.sysop import routes
