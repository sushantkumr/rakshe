"""User view methods."""

from flask_login import current_user
from lib.models.users import User
from lib.models.policy import Policy
from lib.models.claim import Claim
from sqlalchemy.sql import func
from lib.policy.views import _check_policy_creatable


def get_dashboard_data():
    """Get dashboard data for current user"""
    rows = (Policy.query.filter(Policy.user_id == current_user.id)
                        .filter(Policy.status == 'Active'))
    active_policies = rows.count()
    total_coverage = (rows.with_entities(func.sum(Policy.coverage_limit)).scalar())

    if total_coverage is None:
        total_coverage = 0
    claims_pending = (Claim.query.filter(Claim.user_id == current_user.id)
                                 .filter(Claim.status == 'Submitted').count())
    try:
        buy_policy = _check_policy_creatable()
    except Exception:
        buy_policy = False

    row = (User.query.filter(User.id == current_user.id).first())
    email_verification = not row.email_verified

    return {
        'activePolicies': str(active_policies),
        'totalCoverage': str(total_coverage),
        'claimsPending': str(claims_pending),
        'buyPolicy': buy_policy,
        'emailVerification': email_verification
    }
