"""Util methods for DB specific operations."""

import bcrypt
import json
from lib.core import config

secret_key = config.get_config()['secret_key']


def hash_password(password, salt=None):
    """Hash password and salt for storing it in DB.

    Use common methods whenever interacting with pw fields.
    """
    if salt is None:
        salt = bcrypt.gensalt().decode()
    combo = password + salt + secret_key
    hash = bcrypt.hashpw(combo.encode('utf-8'), salt.encode('utf-8'))
    return salt, hash.decode()


def to_str(value):
    """Handle special cases while converting to string."""
    if value is None:
        return ''
    elif value is False:
        return 'false'
    elif value is True:
        return 'true'
    return str(value)


def to_dict(sql_result, jsonify=False):
    """An array of or a single sqlalchemy object will be converted to a dict.

    Pass jsonify=True if required.
    """
    def convert_to_dict(obj):
        d = {}
        for column in obj.__table__.columns:
            d[column.name] = to_str(getattr(obj, column.name))
        return d

    if isinstance(sql_result, list):
        result = [convert_to_dict(i) for i in sql_result]

    else:
        result = convert_to_dict(sql_result)

    if jsonify:
        return json.dumps(result)
    else:
        return result
