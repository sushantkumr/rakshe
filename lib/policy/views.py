"""Policy view methods."""

from flask_login import current_user

from lib.core.config import get_config
from lib.core.constants import get_long_string, GETH_IPC_PATH
from lib.core.exceptions import UserError, bootbox_error
from lib.models import db
from lib.models.misc import Setting
from lib.models.policy import Dapp, Contract, Policy
from lib.models.users import User
from lib.models.utils import to_dict

from web3 import Web3, IPCProvider
from dateutil import relativedelta
from sqlalchemy.sql import func

import datetime
import json
import math
import requests


def get_approved_dapps(dapp_id=None):
    """List of all DApps that are available for insurance."""

    _check_policy_creatable(dapp_id=None)
    dapps = (Dapp.query
             .filter(Dapp.total_issued < Dapp.total_coverage_limit)
             .filter(Dapp.approved)
             .all())

    if dapp_id:
        dapps = (Dapp.query
                 .filter(Dapp.total_issued < Dapp.total_coverage_limit)
                 .filter(Dapp.approved)
                 .filter(Dapp.id == dapp_id)
                 .all())

        # If a wrong dapp_id is passed as a parameter
        if not len(dapps):
            raise UserError('DApp not found')

    to_remove = []

    # Get the coverage for active policies
    total_issued = _get_total_issued()
    global_coverage_limit = Setting.get_value_by_section_option('policy', 'global_coverage_limit', cast=float)
    option_1 = round(global_coverage_limit - total_issued, 3)

    for i in range(len(dapps)):
        option_2 = round(dapps[i].total_coverage_limit - dapps[i].total_issued,
                         3)

        """ Minimum of (Coverage remaining from all policies,
        Coverage remaining from current policy, Current policy's max)
        """
        available = min(option_1, option_2, dapps[i].policy_coverage_max)
        if available < dapps[i].policy_coverage_min:
            to_remove.append(i)
            continue

        dapps[i].policy_coverage_max = available

    # Remove the Dapps whose coverage is less than 'policy_coverage_min' 
    for i in reversed(to_remove):
        dapps.pop(i)

    dapps = to_dict(dapps)

    # External policies will have only one DApp
    if dapp_id:
        dapps = dapps[0]

    # TODO: Don't mess with dapp objects directly, make copies so that their
    # original limits stay the same.
    db.db_session.rollback()
    return dapps


def _check_policy_creatable(dapp_id=None, coverage_limit=None):
    """Check if a NEW policy can be created or not.

    Raises UserError if it's not possible.
    """
    externaluser_flag = False
    try:
        user_id = current_user.id
    except:
        user_row = (User.query
                    .filter(User.name == 'EXTERNALPOLICY')
                    .first())

        user_id = user_row.id
        externaluser_flag = True

    if user_id and not externaluser_flag:

        # Check if the user has any active policies
        user_active_policies = (Policy.query
                                .filter(Policy.status == 'Active')
                                .filter(Policy.user_id == user_id)
                                .all())

        max_policies_per_user = Setting.get_value_by_section_option(
            'policy', 'max_policies_per_user', cast=int
        )
        if len(user_active_policies) >= max_policies_per_user:
            raise UserError(get_long_string('max-policies-per-user'))

    # Check for Dapps that are approved have policies issued less than coverage limit
    dapps = (Dapp.query
             .filter(Dapp.total_issued < Dapp.total_coverage_limit)
             .filter(Dapp.approved)
             .all())

    total_issued = _get_total_issued()

    global_coverage_limit = Setting.get_value_by_section_option('policy', 'global_coverage_limit', cast=float)
    if len(dapps) == 0 or total_issued >= global_coverage_limit:
        raise UserError(get_long_string('out-of-policies'))

    if dapp_id and coverage_limit:
        dapp = Dapp.query.get(dapp_id)
        if not dapp:
            raise UserError('DApp with given id not found.')

        if dapp.total_issued + coverage_limit >= dapp.total_coverage_limit:
            raise UserError(get_long_string('dapp-out-of-policies'))
        elif coverage_limit > dapp.policy_coverage_max:
            raise UserError('Coverage limit exceeds policy limit.')
        elif coverage_limit < dapp.policy_coverage_min:
            raise UserError('Coverage limit is lower than policy limit.')

    return True


def _get_total_issued():
    """ Get the coverage for active policies
    """
    total_issued = (db.db_session
                    .query(func.sum(Policy.coverage_limit))
                    .filter(Policy.status == 'Active')
                    .one())

    return total_issued[0] or 0


def get_contract_info(dapp_id):
    """Return all active contracts of a DApp."""
    dapp = Dapp.query.get(dapp_id)

    if not dapp:
        raise UserError('DApp not found.')

    contracts = (Contract.query
                 .filter(Contract.dapp_id == dapp_id)
                 .all())

    return to_dict(contracts)


def get_policy_details(id):
    """Return policy information."""
    policy = Policy.query.get(id)

    try:
        user_id = current_user.id
    except:
        user_row = (User.query
                    .filter(User.name == 'EXTERNALPOLICY')
                    .first())

        user_id = user_row.id

    if not policy or policy.user_id != user_id:
        raise UserError('Policy with given id not found')

    policy = to_dict(policy)
    policy['contracts'] = json.loads(policy['contracts'])

    dapp = Dapp.query.get(policy['dapp_id'])

    return {
        'policy': policy,
        'dapp': to_dict(dapp)
    }


def get_policies_list():
    """Return a list of policies of the current user."""
    raw = (db.db_session
             .query(Policy.id, Policy.status, Policy.created_at,
                    Policy.policy_activation_time, Policy.fee_received,
                    Policy.policy_termination_time, Dapp.name)
             .filter(Policy.user_id == current_user.id)
             .filter(Dapp.id == Policy.dapp_id)
             .all())

    keys = ['id', 'status', 'created_at', 'policy_activation_time',
            'fee_received', 'policy_termination_time', 'dapp_name']
    policies = [dict(zip(keys, result)) for result in raw]

    return policies


@bootbox_error
def check_fee_paid(tx_hash, policy_id):
    """Check if correct fee has been paid by the correct address.

    If all conditions are satisfied the policy will become active.
    """
    externaluser_flag = False
    policy = Policy.query.get(policy_id)

    try:
        user_id = current_user.id
    except:
        user_row = (User.query
                    .filter(User.name == 'EXTERNALPOLICY')
                    .first())

        user_id = user_row.id
        externaluser_flag = True

    if not policy or policy.user_id != user_id:
        raise UserError('Policy not found')

    # Check if the tx hash has been used for some other policy already
    past_policies = (Policy.query
                     .filter(Policy.tx_hash == tx_hash)
                     .all())
    if len(past_policies) > 0:
        raise UserError(get_long_string('tx-paid-for-another-policy'))

    network_name = Setting.get_value_by_section_option('global',
                                                       'network_name')

    if network_name == 'mainnet':
        api_sub_domain = 'api.'
    else:
        api_sub_domain = 'api-' + network_name + '.'

    url = 'https://' + api_sub_domain + 'etherscan.io/api'

    params = {
        'module': 'proxy',
        'action': 'eth_getTransactionByHash',
        'txhash': tx_hash,
        'apikey': get_config()['etherscan']
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception({'code': 'Non 200'})
        data = response.json()
    except Exception as e:
        message = ('Error connecting to GETH node. '
                   'Please try again in a few minutes.')

        if len(e.args) > 0 and e.args[0].get('code', None):
            message += ' Code: ' + e.args[0].get('code', '')

        raise UserError(message)

    error = data.get('error', None)
    if error:
        raise UserError(error['message'])

    result = data.get('result', None)
    if result is None:
        raise UserError(get_long_string('tx-not-found'))

    if result.get('blockNumber', None) is None:
        raise UserError(get_long_string('tx-not-mined'))

    sender = result['from']
    to = result['to']
    fee_in_wei = int(result['value'], 16)
    fee_in_eth = fee_in_wei / 1e18

    if sender != policy.insuree_address:
        raise UserError('The insuree and tx sender address does not match.')

    # BLAAAA Enter the correct address here and remove 'and False'
    if to != '0x4de22441e9bdc4901235d9c2b83947c562114355' and False:
        raise UserError('The fee recipient address and the tx recipient '
                        'address do not match.')

    # TODO: Replace with math.is_close when server is updated to python 3.6
    # Check if fee paid is close enough to what we were expecting
    # BLAAAA Remove 'and False'
    if abs(fee_in_eth - policy.fee) > 1e-5 and False:
        raise UserError('Fee expected is not the same as transferred amount. '
                        'Please try again.')

    policy.tx_hash = tx_hash
    policy.fee_received = True

    return_flag = False
    dapp = Dapp.query.get(policy.dapp_id)

    global_coverage_limit = Setting.get_value_by_section_option('policy', 'global_coverage_limit', cast=float)
    if dapp.total_issued >= dapp.total_coverage_limit or \
            _get_total_issued() >= global_coverage_limit:
        policy.status = 'Pending Refund'
        policy.note = ('Due to delay in receiving fees your policy application'
                       ' has been rejected. Your fee will be refunded soon.')

        return_flag = True

    # Check for EXTERNALUSER must not be made
    user_policies = (Policy.query
                     .filter(Policy.status == 'Active')
                     .filter(Policy.user_id == user_id)
                     .filter(not externaluser_flag)
                     .all())
    if len(user_policies) >= Setting.get_value_by_section_option('policy', 'max_policies_per_user', cast=int):
        policy.status = 'Pending Refund'
        policy.note = get_long_string('max-policies-per-user-fee-refund')
        return_flag = True

    if return_flag:
        db.db_session.add(policy)
        return ''

    try:
        web3 = Web3(IPCProvider(GETH_IPC_PATH))

        address = '0x4de22441e9bdc4901235d9c2b83947c562114355'

        # TODO: Figure out a better way to automate these signatures.
        # Private keys are not safe in the current way.
        signature = web3.personal.sign(policy.message, address, '')

        policy.insurer_address = address
        policy.insurer_signature = signature

        now = datetime.datetime.now()
        policy_duration = relativedelta.relativedelta(days=90)

        policy.policy_activation_time = now
        policy.policy_termination_time = now + policy_duration
        policy.status = 'Active'
        dapp.total_issued += policy.coverage_limit
    except:
        policy.status = 'Pending Signature'
        policy.policy_activation_time = None
        policy.policy_termination_time = None
        policy.insurer_signature = ''
        policy.note = ('An error occurred while signing the message '
                       'automatically. Please contact us to get your'
                       ' warranty activated.')

    db.db_session.add(dapp)
    db.db_session.add(policy)

    # Reject all other policies
    policies = (Policy.query
                .filter(Policy.user_id == user_id)
                .filter(Policy.id != policy.id)
                .filter(Policy.status == 'Submitted')
                .all())

    for policy in policies:
        policy.status = 'Rejected'
        policy.note = get_long_string('max-policies-per-user')
        db.db_session.add(policy)

    return ''


def _get_message(dapp_name, contract_addresses, coverage_limit,
                 fee, insuree_address):
    """Return the message that is used for signatures."""
    padding = ' *************************************************** '
    message_head = ''.join([
        'I agree to the terms and conditions mentioned in the New Warranty '
        'page on Rakshe.com. I understand that coverage is active only ',
        'after I receive a signature on this message by a Rakshe underwriter.',
        padding,
        'Warranty information: ',
    ])

    dapp_name = 'DApp name: ' + dapp_name

    coverage_message = ' Coverage Limit: ' + str(coverage_limit) + ' ETH.'
    fee_message = ' Fee: ' + str(fee) + ' ETH'

    # Generate one of the following patterns depending on number of contracts:
    # 0x0
    # 0x0 and 0x0
    # 0x0, 0x0 and 0x0
    addresses = len(contract_addresses)
    contracts = ''
    for i, address in enumerate(contract_addresses):
        contracts += address
        if addresses > 1:
            if i == addresses - 2:
                contracts += ' and '
            elif i < addresses - 2:
                contracts += ', '

    contracts_covered = ' Contracts covered: ' + contracts
    signed_by_insuree = ' Signed by address (warranty buyer): ' + insuree_address

    message = ''.join([
        message_head,
        padding,
        dapp_name,
        padding,
        contracts_covered,
        padding,
        coverage_message,
        fee_message,
        padding,
        signed_by_insuree,
    ])

    live_status = Setting.get_value_by_section_option('global', 'live_status', cast=int)
    if live_status == 1:
        test_site_notice = 'WARNING: THIS IS A TEST SITE FOR DEMONSTRATION ONLY. REAL ETH WILL NOT BE COLLECTED AS FEE AND A REAL WARRANTY WILL NOT BE ISSUED.'
        message = ''.join([
            test_site_notice,
            padding,
            message,
        ])

    return message


def _get_address_or_github_source(contract):
    if contract.address:
        return contract.address
    elif contract.github_source:
        return contract.github_source
    else:
        return ''


def submit_policy_application(dapp_id, contract_addresses, coverage_limit,
                              insuree_address, signature):
    """Verify signature and create a new policy.

    Policy *SHOULD NOT* be active in this step.
    """
    _check_policy_creatable(dapp_id, coverage_limit)

    dapp = Dapp.query.get(dapp_id)
    contracts = (Contract.query
                 .filter(Contract.dapp_id == dapp_id)
                 .all())
    contracts = [_get_address_or_github_source(c) for c in contracts]

    if set(contracts) != set(contract_addresses):
        raise UserError(get_long_string('contract-set-mismatch'))

    fee = max(0.0001, math.ceil(coverage_limit * 10000) / 1000000)
    message = _get_message(dapp.name, contract_addresses, coverage_limit,
                           fee, insuree_address)

    web3 = Web3(IPCProvider(GETH_IPC_PATH))
    address = web3.personal.ecRecover(message, signature)

    if address != insuree_address:
        raise UserError('Signature could not be verified please try again.')

    try:
        user_id = current_user.id
    except:
        user_row = (User.query
                    .filter(User.name == 'EXTERNALPOLICY')
                    .first())

        user_id = user_row.id

    policy = Policy(dapp_id, contracts, message, signature, insuree_address,
                    user_id, coverage_limit, fee, status='Submitted')
    db.db_session.add(policy)

    return {'id': policy.id}
