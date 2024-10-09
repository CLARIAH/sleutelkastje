from functools import wraps

from flask import jsonify


def permission(func, resource=None):
    """
    Check permission
    :param func:
    :param resource:
    :return:
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if resource in kwargs:
                value = kwargs[resource]
                valid = func(value)
            else:
                valid = func()
            if not valid:
                return jsonify({'error': 'Permission denied'}), 403
            return f(*args, **kwargs)

        return decorated

    return decorator
