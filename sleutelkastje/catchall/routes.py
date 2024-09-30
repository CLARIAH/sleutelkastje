from sleutelkastje.authentication import oidc_auth
from sleutelkastje.catchall import bp


@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
@oidc_auth.oidc_auth('default')
def catch_all(path):
    """
    Returns the front-end React application.
    :param path:
    :return:
    """
    print("Catchall! Returning static file")
    return bp.send_static_file('index.html')
