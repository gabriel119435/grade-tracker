from dataclasses import dataclass

from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.constants import DEFAULT_LOCALE, LOCALES
from app.db import Base


@dataclass
class AuthUser(UserMixin):
    # flask-login needs a user object for login_user() and current_user. a User row can't be that object.
    # its db session closes right away, which crashes on relationships. this copy holds only plain fields.
    id: int
    username: str
    role: str
    password_hash: str
    locale: str

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
            locale=user.locale
        )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(Enum("admin", "teacher", "student"))
    locale: Mapped[str] = mapped_column(
        # default sqlalchemy level, server_default db level
        Enum(*LOCALES), default=DEFAULT_LOCALE, server_default=DEFAULT_LOCALE
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    # passive_deletes: one DELETE on the parent, sqlite cascades the children, o(1) in python.
    # without it sqlalchemy loads every child first, o(n).
    subcategories: Mapped[list["Subcategory"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="Subcategory.id",
        passive_deletes=True
    )


class Subcategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))

    # sub names can repeat at different categories, not under same one
    __table_args__ = (UniqueConstraint("category_id", "name"),)

    # python-only access to the category row through `category_id`, no db column
    category: Mapped["Category"] = relationship(back_populates="subcategories")


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
    subcategory: Mapped["Subcategory"] = relationship()
