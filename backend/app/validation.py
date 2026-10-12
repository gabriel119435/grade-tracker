from flask import abort

from app.constants import NAME_MAX_LENGTH, NAME_WORD_MAX_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH


def password_error(password):
    """
    checks password length rules.
    password: str raw password.
    returns: str | None error code, None if valid.
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return "password_too_short"
    if len(password) > PASSWORD_MAX_LENGTH:
        return "password_too_long"
    return None


def validate_word_size(text):
    if any(len(word) > NAME_WORD_MAX_LENGTH for word in text.split()):
        abort(400, "word_too_long")


# category and subcategory names: length and word size, caller checks empty first
def validate_name(name):
    if len(name) > NAME_MAX_LENGTH:
        abort(400, "name_too_long")
    validate_word_size(name)
