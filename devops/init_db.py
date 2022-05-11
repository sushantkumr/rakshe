"""Initialize the DB with seed data."""

import os
import sys

sys.path.append(os.getcwd())

from lib.core.config import get_config # noqa
from lib.models import db # noqa
from lib.models.audits import AuditApplication # noqa
from lib.models.policy import Dapp, Contract, Policy # noqa
from lib.models.claim import Claim # noqa
from lib.models.users import User, JoinUs # noqa
from lib.models.misc import Setting # noqa


try:
    os.remove(get_config()['connection_string'][10:])
except:
    # If it doesn't exist already
    pass

db.init_db()

user = User('123456789012', 'rohith', False, 'abc@abc.com')
user.email_verified = True
db.db_session.add(user)

user = User('123456789012', 'sushant', False, 'xyz@abc.com')
user.email_verified = True
db.db_session.add(user)

user = User('123456789012', 'EXTERNALPOLICY', False, 'xyz@abc.com')
user.email_verified = True
db.db_session.add(user)

db.db_session.commit()

dapp = Dapp('etheroll', 'http://etheroll.com', id='1', approved=True,
            total_coverage_limit=1000, policy_coverage_max=50,
            policy_coverage_min=0.1)
db.db_session.add(dapp)

contract = Contract(dapp.id, '0x805129c7144688224c122c924e3855d5b4fa01d8')
db.db_session.add(contract)

dapp = Dapp('kitties', 'http://kitties.com', id='2', approved=True,
            total_coverage_limit=1000, policy_coverage_max=50,
            policy_coverage_min=0.1)
db.db_session.add(dapp)

contract = Contract(dapp.id, '0x0000000000000000000000000000000000000000')
db.db_session.add(contract)

contract = Contract(dapp.id, '0x0000000000000000000000000000000000000001')
db.db_session.add(contract)

dapp = Dapp('EthLend', 'http://ethlend.io', id='3', approved=True,
            total_coverage_limit=1000, policy_coverage_max=50,
            policy_coverage_min=0.1)
db.db_session.add(dapp)

ethlend = 'https://github.com/ETHLend/ICO_SmartContract/blob/8134d04372d3145e108d025048eef794d79d0a40/contracts/EthLendICO.sol'  # noqa
contract = Contract(dapp.id, github_source=ethlend)
db.db_session.add(contract)

network_id = Setting('global', 'network_id', '4', '')
db.db_session.add(network_id)

network_name = Setting('global', 'network_name', 'rinkeby', '')
db.db_session.add(network_name)

live_status = Setting('global', 'live_status', '1', '0: live, 1: demo')
db.db_session.add(live_status)

global_coverage_limit = Setting('policy', 'global_coverage_limit', '3000')
db.db_session.add(global_coverage_limit)

max_policies_per_user = Setting('policy', 'max_policies_per_user', '20')
db.db_session.add(max_policies_per_user)

db.db_session.commit()
