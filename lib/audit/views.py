"""Go away linter."""

from flask_login import current_user
from sqlalchemy import desc

from lib.models import db
from lib.models.utils import to_dict
from lib.models.audits import AuditApplication
from lib.core.exceptions import UserError

import sqlalchemy


def submit_for_audit(name, source_code_link, dapp_link, dapp_description):
    """Create an application for contract audit."""
    if current_user.email == '' or not current_user.email_verified:
        raise UserError({'type': 'alert-error',
                         'message': 'Email id has not been verified. '
                                    'Your email id has to be verified before '
                                    'a contract can be submitted for audit.'})

    # Possible states of a submitted contract are:
    # Submitted, Audit in progress, Audit complete, Approved, Cancelled etc
    status = 'Submitted'
    row = (AuditApplication.query
           .filter(AuditApplication.name == name)
           .filter(AuditApplication.user_id == current_user.id)
           .filter(AuditApplication.status == 'Submitted')
           .first())

    if row:
        raise UserError('A contract with this name has already '
                        'been submitted and is pending audit.')

    audit = AuditApplication(
        current_user.id,
        name,
        source_code_link,
        dapp_link,
        dapp_description[:1000],
        status
    )
    db.db_session.add(audit)

    return {'id': audit.id}


def get_application_details(id):
    """Return details of application submitted for audit."""
    application = AuditApplication.query.get(id)

    if not (application and application.user_id == current_user.id):
        raise UserError('Application not found.')

    return to_dict(application)


def cancel_application(id):
    """Cancel an application that has been submitted for audit.

    This method can be called only if the application is in certain states.
    Ensure that the list of cancellable states is common between the front
    and back end.
    """
    application = AuditApplication.query.get(id)

    if not (application and application.user_id == current_user.id):
        raise UserError('Application not found.')

    application.status = 'Cancelled'
    db.db_session.add(application)
    return to_dict(application)


def get_applications_list():
    """Return list of applications that have been submitted for audit."""
    case = sqlalchemy.sql.expression.case(
        (
            (AuditApplication.status != 'Cancelled', 1),
            (AuditApplication.status == 'Cancelled', 2),
        )
    )
    applications = (AuditApplication.query
                    .filter(AuditApplication.user_id == current_user.id)
                    .order_by(case)
                    .order_by(desc(AuditApplication.created_at))
                    .all())
    return to_dict(applications)
