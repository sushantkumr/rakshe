"""View methods for DApp listing.

Do not expect a user to be logged in in these methods.
"""

from lib.models import db
from lib.core.exceptions import UserError
from lib.models.list_dapp import ListContract, ListDapp

from sqlalchemy import text


def get_contract_usage_data(address=None, contract=None):
    """Return usage stats of the given address."""
    if contract is None:
        contract = ListContract.query.get(address)
        if not contract:
            raise UserError('Contract not found')
    else:
        address = contract.address

    query = '''
        select
            date(time_stamp) as date,
            sum(gas_used) as total_gas_used,
            count(*) as transactions
        from
            list_raw_transaction
        where
            contract = "{contract_address}"
        group by
            date(time_stamp)
        order by
            date;
        '''.format(contract_address=address)

    query = text(query)
    result = db.engine.execute(query)
    rows = result.fetchall()

    result = {
        'labels': [],
        'gasUsed': [],
        'txCount': []
    }
    for row in rows:
        result['labels'].append(row[0])
        result['gasUsed'].append({
            'x': row[0],
            'y': row[1]
        })
        result['txCount'].append({
            'x': row[0],
            'y': row[2]
        })

    return result


def get_dapp_usage_data(dapp_id):
    """Return usage statistics of the DApp."""
    dapp = ListDapp.query.get(dapp_id)
    if not dapp:
        raise UserError('DApp with given id not found.')

    # Add support for multiple contracts per DApp
    contract = (ListContract.query
                .filter(ListContract.dapp_id == dapp.id)
                .first())

    usage = get_contract_usage_data(contract=contract)
    return usage
