from dataclasses import dataclass

from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey, Index, UniqueConstraint, delete, select, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import DEFAULT_LOCALE, LOCALES
from app.db import Base


@dataclass
class AuthUser(UserMixin):
    # flask-login needs a user object for login_user() and current_user, this plain copy is that object.
    # it adds get_id() below, which User lacks, and keeps orm rows out of current_user.
    id: int
    username: str
    role: str
    password_hash: str
    locale: str
    arena_id: int

    def get_id(self):
        # stored in the session cookie as "<id> <last 10 hash chars>". load_user rejects it once the password changes.
        return f"{self.id} {self.password_hash[-10:]}"

    @classmethod
    def from_user(cls, user):
        return cls(
            id=user.id,
            username=user.username,
            role=user.role,
            password_hash=user.password_hash,
            locale=user.locale,
            arena_id=user.arena_id,
        )


class Arena(Base):
    __tablename__ = "arenas"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    arena_id: Mapped[int] = mapped_column(ForeignKey("arenas.id", ondelete="CASCADE"))
    username: Mapped[str]
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(Enum("admin", "teacher", "student"))
    locale: Mapped[str] = mapped_column(
        # default sqlalchemy level, server_default db level
        Enum(*LOCALES),
        default=DEFAULT_LOCALE,
        server_default=DEFAULT_LOCALE,
    )

    __table_args__ = (
        UniqueConstraint("arena_id", "username"),
        # one admin per arena, enforced by the db: unique arena_id among admin rows only
        Index(
            "ux_users_one_admin_per_arena",
            "arena_id",
            unique=True,
            sqlite_where=text("role = 'admin'"),
        ),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    arena_id: Mapped[int] = mapped_column(ForeignKey("arenas.id", ondelete="CASCADE"))
    name: Mapped[str]

    # same category name allowed in different arenas, not in the same one
    __table_args__ = (UniqueConstraint("arena_id", "name"),)

    # passive_deletes: one DELETE on the parent, sqlite cascades the children, o(1) in python.
    # without it sqlalchemy loads every child first, o(n).
    subcategories: Mapped[list[Subcategory]] = relationship(
        back_populates="category", cascade="all, delete-orphan", order_by="Subcategory.id", passive_deletes=True
    )


class Subcategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))

    # sub names can repeat at different categories, not under same one
    __table_args__ = (UniqueConstraint("category_id", "name"),)

    # python-only access to the category row through `category_id`, no db column
    category: Mapped[Category] = relationship(back_populates="subcategories")


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[float]
    date: Mapped[str]  # stored as iso string, sqlite has no native date type
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    # last teacher who created or edited the grade. any teacher may edit or delete any grade
    # deleting a teacher deletes every grade they last created or edited: every grade always has an author
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id", ondelete="CASCADE"))

    __table_args__ = (
        # one grade per student per subcategory per day
        UniqueConstraint("student_id", "subcategory_id", "date"),
        # count grades per teacher
        Index("ix_grades_teacher_id", "teacher_id"),
        # cascade deletion of a sub category
        Index("ix_grades_subcategory_id", "subcategory_id"),
    )

    # python-only access to the subcategory row through `subcategory_id`, no db column
    subcategory: Mapped[Subcategory] = relationship()


def wipe(session, arena_id):
    # deletes arena's grades, subcategories, categories and non admin users.
    user_ids = select(User.id).where(User.arena_id == arena_id)
    category_ids = select(Category.id).where(Category.arena_id == arena_id)
    session.execute(delete(Grade).where(Grade.student_id.in_(user_ids)))
    session.execute(delete(Subcategory).where(Subcategory.category_id.in_(category_ids)))
    session.execute(delete(Category).where(Category.arena_id == arena_id))
    session.execute(delete(User).where(User.arena_id == arena_id, User.role != "admin"))
