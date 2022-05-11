"""Claim view methods."""

from flask_login import current_user
from web3 import Web3, IPCProvider

from lib.core.constants import GETH_IPC_PATH
from lib.core.exceptions import UserError
from lib.models import db
from lib.models.policy import Dapp, Contract, Policy
from lib.models.claim import Claim
from lib.models.utils import to_dict


def get_claimable_policy_list():
    """Return a list of policies of the current user."""
    claimable_states = ['Active', 'Open to Claims']
    raw = (db.db_session
             .query(Policy.id, Policy.status, Policy.created_at,
                    Policy.policy_activation_time,
                    Policy.policy_termination_time, Dapp.name, Policy.dapp_id,
                    Dapp.website)
             .filter(Policy.user_id == current_user.id)
             .filter(Dapp.id == Policy.dapp_id)
             .filter(Policy.status.in_(claimable_states))
             .all())

    keys = ['id', 'status', 'created_at', 'policy_activation_time',
            'policy_termination_time', 'dapp_name', 'dapp_id', 'website']
    policies = [dict(zip(keys, result)) for result in raw]

    for i in range(len(policies)):
        policy = policies[i]
        message = ' - '.join([
            policy['dapp_name'],
            'P' + str(policy['id'][-4:]),
            policy['status']
        ])
        policies[i]['dropdown_message'] = message

    return policies


def get_contract_info(dapp_id):
    """Return all active contracts of a DApp."""
    dapp = Dapp.query.get(dapp_id)

    if not dapp:
        raise UserError('DApp not found.')

    contracts = (Contract.query
                 .filter(Contract.dapp_id == dapp_id)
                 .all())

    return to_dict(contracts)


def get_claims_list():
    """Return a list of claims of the current user."""
    raw = (db.db_session
             .query(Claim.id, Claim.status, Claim.created_at,
                    Claim.claim_settlement_time, Dapp.name, Claim.policy_id)
             .filter(Claim.user_id == current_user.id)
             .filter(Dapp.id == Claim.dapp_id)
             .all())

    keys = ['id', 'status', 'created_at', 'claim_settlement_time',
            'dapp_name', 'policy_id']
    claims = [dict(zip(keys, result)) for result in raw]

    return claims


def get_claim_details(id):
    """Return claim information."""
    claim = Claim.query.get(id)

    if not claim or claim.user_id != current_user.id:
        raise UserError('Claim with given id not found')

    claim = to_dict(claim)
    dapp = Dapp.query.get(claim['dapp_id'])

    return {
        'claim': claim,
        'dapp': to_dict(dapp)
    }


def _get_message(policy_id, insuree_address):
    """Return the message that is used for signatures."""
    padding = ' ************************************************** '
    message_head = ''.join([
        'I agree to the terms and conditions mentioned in the New Claim '
        'page on Rakshe.com. I understand that claim can be delayed unless'
        ' accepted.',
        padding,
        'Claim information: ',
    ])

    policy_id_msg = 'Warranty ID: ' + policy_id
    signed_by_insuree = ' Signed by address (warranty holder): ' + insuree_address

    message = ''.join([
        message_head,
        padding,
        padding,
        policy_id_msg,
        padding,
        signed_by_insuree,
    ])

    return message


def raise_claim(policy_id, insuree_address, signature, claim_remark):
    """Verify signature and creates a new claim."""
    policy = Policy.query.get(policy_id)

    if not policy:
        raise UserError('Policy with given id not found.')

    message = _get_message(policy_id, insuree_address)

    web3 = Web3(IPCProvider(GETH_IPC_PATH))
    address = web3.personal.ecRecover(message, signature)

    if address != policy.insuree_address:
        raise UserError('Please use the same address which was used to create the policy to sign the claim application.')

    elif address != insuree_address:
        raise UserError('Signature could not be verified please try again.')

    claim = Claim(policy.id, policy.dapp_id, message, signature,
                  insuree_address, current_user.id, claim_remark)
    db.db_session.add(claim)

    return {'id': claim.id}
