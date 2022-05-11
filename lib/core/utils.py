"""Util methods for miscellaneous operations.
    1. Exception handling
    2. Sending emails
    3. Generating/Verifying tokens
"""

import sendgrid
from sendgrid.helpers.mail import Email, Content, Substitution, Mail
from lib.core import config
import bcrypt
from lib.models.users import Token
from lib.models import db
from datetime import datetime, timedelta
from lib.core.exceptions import UserError
import urllib.request as urllib

secret_key = config.get_config()['secret_key']
sendgird_apikey = config.get_config()['sendgrid']
sendgrid_template_id = config.get_config()['sendgrid_template_id']


def process_error(e):
    args = e.args

    # No params
    if len(args) == 0:
        return({'success': False, 'message': ''})

    # Simple error
    if len(args) == 1 and type(args[0]) == str:
        return({'success': False, 'message': args[0]})

    # Multi param
    if len(args) == 2 and type(args[0]) == type(args[1]) == str:
        return({'success': False, 'message': args[1], 'type': args[0]})

    # Expand dict
    if len(args) == 1 and type(args[0]) == dict:
        # Update it on a different line and then return / return.
        # Don't try to save lines, it won't work cuz update() returns
        # None and modifies the existing obj :P
        args[0].update({'success': False})

        # If the dict doesn't have a 'message' key,
        # set it to maintain consistency
        if not args[0].get('message', None):
            args[0]['message'] = ''
        return(args[0])


def send_email(from_email, to_email, subject, link, messages):
    sg = sendgrid.SendGridAPIClient(apikey=sendgird_apikey)
    from_email = Email(from_email)
    to_email = Email(to_email)
    content = Content("text/html", '<a href="http://rakshe.com">rakshe</a>')
    mail = Mail(from_email, subject, to_email, content)
    (mail.personalizations[0].add_substitution(Substitution
                                               ('-message-', messages[0])))
    mail.personalizations[0].add_substitution(Substitution('-link-', link))
    (mail.personalizations[0].add_substitution(Substitution
                                               ('-button_text-', messages[1])))
    mail.template_id = sendgrid_template_id

    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except urllib.HTTPError as e:
        print(e.read())


def generate_token(plain_text, user_id, flag):
    """Hash token and salt for storing it in DB."""
    salt = bcrypt.gensalt().decode()
    combo = plain_text + salt + secret_key
    hash = bcrypt.hashpw(combo.encode('utf-8'), salt.encode('utf-8'))
    row = Token(hash=hash, salt=salt, user_id=user_id, flag=flag)
    db.db_session.add(row)
    return hash.decode()


def verify_token(token):
    """Token verification"""
    row = Token.query.filter(Token.hash == token.encode('utf-8')).first()

    if row.flag == 'email_verification':
        message = 'Verification'
    else:
        message = 'Password-Reset'

    if row is None:
        raise UserError("Invalid token")
    elif row.created_at > datetime.now() + timedelta(hours=24):
        raise UserError(message + ' link has expired.')
    elif row.used:
        raise UserError(message + ' link has already been used.')
    else:
        row.used = True
        return row.user_id, row.flag
