from dataclasses import dataclass

from flask_login import UserMixin
from sqlalchemy import Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


@dataclass
class AuthUser(UserMixin):
    # plain dataclass copy of user fields, needed because get_session() closes the session after each request, detaching the orm object
    # flask-login holds the user across requests so accessing a detached user would raise DetachedInstanceError; this stays alive freely
    id: int
    username: str
    role: str
    password_hash: str
    locale: str


class User(UserMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    role: Mapped[str] = mapped_column(Enum("admin", "teacher", "student"))
    locale: Mapped[str] = mapped_column(
        # default sqlalchemy level, server_default db level
        Enum("en", "pt-br"), default="pt-br", server_default="pt-br"
    )

    received_grades = relationship(
        "Grade",
        foreign_keys="Grade.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    given_grades = relationship(
        "Grade",
        foreign_keys="Grade.teacher_id",
        back_populates="teacher",
        cascade="all, delete-orphan",
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    subcategories = relationship("Subcategory", back_populates="category", cascade="all, delete-orphan", order_by='Subcategory.id')


class Subcategory(Base):
    __tablename__ = "subcategories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))

    # sub names can repeat at different categories, not under same one
    __table_args__ = (UniqueConstraint("category_id", "name"),)

    category = relationship("Category", back_populates="subcategories")
    grades = relationship("Grade", back_populates="subcategory", cascade="all, delete-orphan")


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[float]
    date: Mapped[str]  # stored as iso string, sqlite has no native date type
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id", ondelete="CASCADE"))

    __table_args__ = (
        # one grade per student per subcategory per day
        UniqueConstraint("student_id", "subcategory_id", "date"),
        # read grades by student ordered by date
        Index("ix_grades_student_date", "student_id", "date"),
        # count grades per teacher
        Index("ix_grades_teacher_id", "teacher_id"),
        # cascade deletion of a sub category
        Index("ix_grades_subcategory_id", "subcategory_id"),
    )

    student = relationship("User", foreign_keys=[student_id], back_populates="received_grades")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="given_grades")
    subcategory = relationship("Subcategory", back_populates="grades")
