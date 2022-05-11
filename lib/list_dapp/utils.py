"""Utility functions for listing DApps."""

import sys
sys.path.append('/home/vagrant/code/rakshe')

from lib.models import db
from lib.models.list_dapp import ListRawTransaction, ListContract # noqa
from lib.core.exceptions import UserError

import requests

import time

#flake8: noqa
def _get_transactions_of_contract(address):
    """Fetch all new txs of a contract and update the table."""
    contract = ListContract.query.get(address)

    if not contract:
        raise UserError({'success': False,
                         'message': 'Contract with the given address is '
                         'not present in the database'})

    last_updated = (ListRawTransaction.query
                    .filter(ListRawTransaction.contract == address)
                    .order_by(ListRawTransaction.block_number.desc())
                    .first())

    if last_updated:
        # Txs returned are inclusive of those in start_block so add 1
        # to avoid duplication
        start_block = last_updated.block_number + 1
    else:
        # If we don't have any records of that contract
        start_block = 0

    # start_block = 0

    # url = 'http://ropsten.etherscan.io/api'
    url = 'http://api.etherscan.io/api'
    address = '0x805129c7144688224c122c924e3855d5b4fa01d8'
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': start_block,
        'endblock': '',
        'sort': 'asc',
        'apikey': '7CNDPRS3RPXY69937PPVRJG2WZDD9XWNQ6',
        'page': 1,
        'offset': 10000,
    }
    # params.update({'address': '0x6f040767b93ac959dca4fa8145136eecdbec387a'})
    # params.update({'address': '0x805129c7144688224c122c924e3855d5b4fa01d8'})
    print(params)

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise UserError({'status': False,
                         'message': 'Non-200 response code received'})

    response = response.json()

    if response['message'] == 'No transactions found':
        raise UserError({'status': True,
                         'message': 'No more transactions to import'
                         })
    elif response['message'].lower() != 'ok':
        raise UserError({'status': False,
                         'response': response,
                         'params': params
                         })

    print (len(response['result']))
    for i in response['result']:
        tx = ListRawTransaction(i['hash'], address, int(i['blockNumber']),
                                int(i['gasUsed']), int(i['gasPrice']),
                                int(i['timeStamp']))
        db.db_session.add(tx)

    db.db_session.commit()

    return ''


def _update_contract_transactions(address):
    while True:
        try:
            _get_transactions_of_contract(address)
            time.sleep(3)
            break
        except UserError as e:
            break

_update_contract_transactions('0x805129c7144688224c122c924e3855d5b4fa01d8')
