from flask import Blueprint

bp = Blueprint('sysop', __name__, template_folder='templates')

from sleutelkastje.sysop.models import *
from sleutelkastje.sysop import routes
