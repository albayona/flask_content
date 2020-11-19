from functools import update_wrapper

from flask_jwt_extended import get_jwt_claims
from flask_restful import abort
from werkzeug.security import safe_str_cmp

def role_required(role):
    def decorator(fn):
        def wrapped_function(*args, **kwargs):

            # For authorization er return status code 403
            if not safe_str_cmp(get_jwt_claims(), role):
                abort(403)
            return fn(*args, **kwargs)
        return update_wrapper(wrapped_function, fn)
    return decorator
