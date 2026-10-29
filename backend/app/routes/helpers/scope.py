from flask import abort
from flask_login import current_user


def get_in_arena(session, model, row_id):
    # another arena's row is the same 404 as a missing one, its existence never leaks
    row = session.get(model, row_id)
    if not row or row.arena_id != current_user.arena_id:
        abort(404, "not_found")
    return row
