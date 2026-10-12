from functools import wraps

from flask import abort
from flask_login import current_user


# no roles: any logged-in user passes, ex: @require_role()
def require_role(*roles):
    def decorator(f):
        # @wraps preserves __name__ so flask's endpoint registry stays correct when stacking
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401, "unauthorized")
            if roles and current_user.role not in roles:
                abort(403, "forbidden")
            return f(*args, **kwargs)

        return wrapped

    return decorator
