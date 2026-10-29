from flask import Blueprint, abort, jsonify
from flask_login import current_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Category, Subcategory
from app.routes.helpers.decorators import require_role
from app.routes.helpers.payload import get_body, get_int, get_str
from app.routes.helpers.scope import get_in_arena
from app.validation import name_error

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/api/categories")
@require_role("teacher")
def get_categories():
    with get_session() as session:
        categories = session.scalars(
            select(Category)
            .where(Category.arena_id == current_user.arena_id)
            # loads eagerly preventing N+1
            .options(selectinload(Category.subcategories))
            .order_by(Category.id)
        ).all()
    return jsonify(
        [
            {
                "id": c.id,
                "name": c.name,
                # already sorted by subcat.id in models.py cat's definition
                "subcategories": [{"id": s.id, "name": s.name} for s in c.subcategories],
            }
            for c in categories
        ]
    )


@categories_bp.route("/api/categories", methods=["POST"])
@require_role("teacher")
def create_category():
    data = get_body()
    name = get_str(data, "name", "").strip()
    if not name:
        abort(400, "name_required")

    error = name_error(name)
    if error:
        abort(400, error)

    try:
        with get_session(write=True) as session:
            session.add(Category(name=name, arena_id=current_user.arena_id))
        return jsonify({"message": "created"}), 201
    except IntegrityError:
        # category names are unique per arena
        abort(409, "category_exists")


@categories_bp.route("/api/categories/<int:category_id>", methods=["DELETE"])
@require_role("teacher")
def delete_category(category_id):
    with get_session(write=True) as session:
        session.delete(get_in_arena(session, Category, category_id))

    return jsonify({"message": "deleted"})


@categories_bp.route("/api/subcategories", methods=["POST"])
@require_role("teacher")
def create_subcategory():
    data = get_body()
    name = get_str(data, "name", "").strip()
    category_id = get_int(data, "category_id")
    if not name or not category_id:
        abort(400, "name_and_category_required")

    error = name_error(name)
    if error:
        abort(400, error)

    try:
        with get_session(write=True) as session:
            get_in_arena(session, Category, category_id)
            session.add(Subcategory(name=name, category_id=category_id))
        return jsonify({"message": "created"}), 201
    except IntegrityError:
        abort(409, "subcategory_exists")


@categories_bp.route("/api/subcategories/<int:subcategory_id>", methods=["DELETE"])
@require_role("teacher")
def delete_subcategory(subcategory_id):
    with get_session(write=True) as session:
        session.delete(get_in_arena(session, Subcategory, subcategory_id))

    return jsonify({"message": "deleted"})
