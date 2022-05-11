"""Profile view methods."""

from flask_login import current_user
from flask import url_for

from lib.core import config
from lib.core.exceptions import UserError
from lib.models import utils
from lib.models.users import User, Token
import lib.core.utils


secret_key = config.get_config()['secret_key']


def submit_for_password_change(old_login_password, new_login_password):
    """Change password."""
    salt, entered_hash = utils.hash_password(old_login_password,
                                             current_user.salt)
    if entered_hash == current_user.hash:
        row = User.query.filter(User.name == current_user.name).first()
        row.salt, row.hash = utils.hash_password(new_login_password)
        return {
            'message': 'Password changed successfully'
        }
    else:
        raise UserError('Current password is incorrect.')


def get_emailid():
    """Return the user's email id if it's available."""
    if not current_user.email_verified:
        email = current_user.email
    else:
        email = ''
    return {
        'email': email
    }


def get_email_verification_status():
    """Return the user's email verification status."""
    # import pudb; pudb.set_trace();
    user_id = current_user.id
    row = (User.query.filter(User.id == user_id)
                     .filter(User.email_verified).first())

    if row:
        return {
            'message': row.email + ' has been verified.'
        }

    check_verification = (Token.query.filter(Token.user_id == user_id)
                                     .filter(Token.flag == 'email_verification') # noqa
                                     .filter(Token.used == False).first())

    if check_verification is not None:
        message = ('An email with a verification link has been sent to '
                   + current_user.email
                   + ' Please check your spam folder if you do not receive'
                   + ' it with in a few minutes.')
        return {
            'message': message
        }


def submit_for_verify_email(email_id):
    """Send verification email."""
    user = (User.query
            .filter(User.email == email_id)
            .filter(User.email_verified)
            .all())
    if current_user.email_verified and current_user.email == email_id:
        raise UserError(current_user.email + ' has been verified.')
    elif user:
        raise UserError('This email id has already been verified by '
                        'another account. Please check the email id '
                        'you have entered.')
    else:
        current_user.email = email_id.lower()
        current_user.email_verified = False
        from_email = 'do-not-reply@rakshe.com'
        to_email = email_id
        subject = 'Email Verification'
        token = lib.core.utils.generate_token(email_id, current_user.id,
                                              'email_verification')
        confirm_url = url_for('external_template_loader', module='profile',
                              file='email_verification', token=token,
                              _external=True)
        (lib.core.utils.send_email(from_email, to_email, subject, confirm_url,
                                   ['verify your email-id',
                                    'Verify Email-id']))
        message = ('An email with a verification link has been sent to '
                   + current_user.email
                   + ' Please check your spam folder if you do not receive'
                   + ' it with in a few minutes.')
        return {
            'message': message
        }


def email_verification(token):
    """Verify a user's email."""
    user_id, flag = lib.core.utils.verify_token(token)
    user = User.query.filter_by(id=user_id).first()
    if user.email_verified:
        return {
            'message': 'This email id has already been verified.'
        }

    if flag == 'email_verification':
        user.email_verified = True
        return {
            'message': 'Email id has been verified successfully.'
        }


def send_password_reset_mail(email_id):
    """Send password reset email if a profile has this as verified emailid."""
    row = User.query.filter(User.email == email_id).first()
    if row is None:
        raise UserError('This Email-id has not been used for registration.')

    if not row.email_verified:
        message = email_id + ' has not been verified'
        raise UserError(message)
    else:
        from_email = 'do-not-reply@rakshe.com'
        to_email = email_id
        subject = 'Password Recovery'
        token = lib.core.utils.generate_token(email_id, row.id,
                                              'password_reset')
        confirm_url = url_for('external_template_loader', module='profile',
                              file='password_reset', token=token,
                              _external=True)
        (lib.core.utils.send_email(from_email, to_email, subject, confirm_url,
                                   ['reset your password', 'Reset Password']))
        message = 'Password recovery mail has been sent to ' + email_id
        return {
            'message': message
        }


def password_reset_verification(token):
    """Reset password."""
    user_id, flag = lib.core.utils.verify_token(token)


def password_change(password, token):
    """Change password."""
    row = Token.query.filter(Token.hash == token.encode('utf-8')).first()
    user_id = row.user_id
    user = User.query.filter(User.id == user_id).first()
    user.salt, user.hash = utils.hash_password(password)
    return {
        'message': 'Password changed successfully'
    }
