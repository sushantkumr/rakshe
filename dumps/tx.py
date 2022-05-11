
# flake8: noqa
from requests import *

base_url = 'http://ropsten.etherscan.io/api'

params = {
    'module': 'account',
    'action': 'txlist',
    'address': '', #0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121a
    'startblock': '', # 0
    'endblock': '', # 99999999
    'sort': 'asc',
    'apikey': '7CNDPRS3RPXY69937PPVRJG2WZDD9XWNQ6'
}
params.update({'address': '0x6f040767b93ac959dca4fa8145136eecdbec387a'})
import pudb; pudb.set_trace()


response = get(base_url, params=params)
result = response.json()['result']



