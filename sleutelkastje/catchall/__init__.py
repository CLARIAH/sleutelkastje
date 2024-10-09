import os

from flask import Blueprint

bp = Blueprint('catchall', __name__, static_folder='/frontend', static_url_path='/')

from sleutelkastje.catchall import routes
