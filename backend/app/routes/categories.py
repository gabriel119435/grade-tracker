from flask import Blueprint, request, jsonify, abort
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Category, Subcategory
from app.routes.helpers.annotations import require_role

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/api/categories")
@require_role("teacher")
def get_categories():
    with get_session() as session:
        categories = (
            session.execute(
                select(Category)
                .options(selectinload(Category.subcategories))
                .order_by(Category.id)
            )
            .scalars()
            .all()
        )
    return jsonify(
        [
            {
                "id": c.id,
                "name": c.name,
                # already sorted from order_by in models.py
                "subcategories": [{"id": s.id, "name": s.name} for s in c.subcategories],
            } for c in categories
        ]
    )


@categories_bp.route("/api/categories", methods=["POST"])
@require_role("teacher")
def create_category():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        abort(400, "name_required")

    if len(name) > 25:
        abort(400, "name_too_long")

    try:
        with get_session(write=True) as session:
            session.add(Category(name=name))
        return jsonify({"message": "created"}), 201
    except IntegrityError:
        abort(409, "category_exists")


@categories_bp.route("/api/categories/<int:category_id>", methods=["DELETE"])
@require_role("teacher")
def delete_category(category_id):
    with get_session(write=True) as session:
        cat = session.get(Category, category_id)
        if not cat:
            abort(404, "not_found")
        session.delete(cat)

    return jsonify({"message": "deleted"})


@categories_bp.route("/api/subcategories", methods=["POST"])
@require_role("teacher")
def create_subcategory():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    category_id = data.get("category_id")
    if not name or not category_id:
        abort(400, "name_and_category_required")

    if len(name) > 25:
        abort(400, "name_too_long")

    try:
        with get_session(write=True) as session:
            session.add(Subcategory(name=name, category_id=int(category_id)))
        return jsonify({"message": "created"}), 201
    except IntegrityError:
        abort(409, "subcategory_exists")


@categories_bp.route("/api/subcategories/<int:subcategory_id>", methods=["DELETE"])
@require_role("teacher")
def delete_subcategory(subcategory_id):
    with get_session(write=True) as session:
        subcategory = session.get(Subcategory, subcategory_id)
        if not subcategory:
            abort(404, "not_found")
        session.delete(subcategory)

    return jsonify({"message": "deleted"})
