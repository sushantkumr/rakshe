import os

CONFIGS = {}

CONFIGS['TEST'] = {
    'connection_string': 'sqlite:////tmp/test.db',
    'secret_key': 'test',
    'host': '127.0.0.1',
    'port': 5000,
    'debug': True,
    'env': 'TEST',
    'login_captcha_secret': '',
    'signup_captcha_secret': '',
    'sendgrid': '',
    'etherscan': '',
}

CONFIGS['DEV'] = {
    'connection_string': 'sqlite:///' + os.getcwd() + '/dev.db',
    'secret_key': 'dev',
    'host': '0.0.0.0',
    'port': 5000,
    'debug': True,
    'env': 'DEV',
    'login_captcha_secret': '6Lcjni4UAAAAAO7s-jgKUW6xr2sVfh0uvjGQKtIZ',
    'signup_captcha_secret': '6LdqpS4UAAAAAGPjpvVk6vzMAEwpiEUXR6lcjJ5X',
    'sendgrid': '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',
    'etherscan': '7CNDPRS3RPXY69937PPVRJG2WZDD9XWNQ6',
    'sendgrid_template_id': '610d1f67-aef5-479f-9544-51f5ad4f1788',
}


def get_config(env=None):
    # No argument given
    if env is None:
        env = os.environ.get('ENV')

    # Environment is invalid
    if env not in CONFIGS.keys():
        env = 'DEV'

    return CONFIGS[env]
