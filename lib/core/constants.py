"""A collections of constants for use throughout the system.

Get some peace from linter.
"""

# flake8: noqa

LONGSTRINGS = {

    'contract-set-mismatch': 'Mismatch in the set of DApp contracts that were approved. Please refresh the page and try again.',

    'dapp-out-of-policies': 'During the alpha release of Rakshe only a limited number of warranties are available to be issued for each DApp and the this limit has been reached for the DApp you wish to insure. Please refresh the page and choose another DApp to insure.',

    'out-of-policies': 'During the alpha release of Rakshe only a limited number of warranties are available to be issued and we have reached the limit. Thank you your interest in our service. Kindly verify your email id and we\'ll inform you when we are fully launched.',

    'max-policies-per-user': 'During the alpha release of Rakshe each user is eligible for only a limited number of warranties issued automatically. Our records indicate that you have already reached this limit. Thank you your interest in our service. Contact us if you would like to get more warranties issued. Kindly verify your email id and we\'ll inform you when we are fully launched.',

    'max-policies-per-user-fee-refund': 'During the alpha release of Rakshe each user is eligible for only a limited number of warranties issued automatically. Our records indicate that you have already reached this limit as a result this warranty has been rejected. Contact us if you would like to get more warranties issued. Fee paid, if any, will be refunded soon. Thank you your interest in our service. Kindly verify your email id and we\'ll inform you when we are fully launched.',

    'tx-paid-for-another-policy': 'This tx hash has already been used to pay fees for another warranty.',

    'tx-not-found': 'The tx with corresponding hash could not be found. Please verify the hash or try again after sometime.',

    'tx-not-mined': 'The tx with corresponding hash is yet to be mined. Please resubmit the hash after the tx has been mined.',

}


GETH_IPC_PATH = '/home/ubuntu/geth.ipc'


def get_long_string(id):
    return LONGSTRINGS.get(id, '')
