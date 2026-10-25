from flask import Blueprint, jsonify
from sqlalchemy import select

from app.db import get_session
from app.models import Arena

arenas_bp = Blueprint("arenas", __name__)


# public: the login picker lists every arena before anyone is logged in
# [{"id": 1, "name": "arena"}], sorted by name
@arenas_bp.route("/api/arenas")
def get_arenas():
    with get_session() as session:
        arenas = session.scalars(select(Arena).order_by(Arena.name)).all()
    return jsonify([{"id": a.id, "name": a.name} for a in arenas])
