from functools import wraps
from flask import abort
from flask.ext.login import current_user


def role_required(role_name):
    def decorator(func):
        @wraps(func)
        def authorize(*args, **kwargs):
            if role_name not in current_user.roles:
                abort(401)  # not authorized
            return func(*args, **kwargs)
        return authorize
    return decorator
