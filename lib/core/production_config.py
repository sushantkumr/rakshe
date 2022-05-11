"""Replaces config.py in the prod environment."""

CONFIGS = {}

master_username = 'M2g5rsZs6b7jdH8H'
password = '2Dn5YxZqpVwmE67cgjWh'
url = 'bux67ptnrzaqk5qdkzam.ctpruaqd4jw5.us-east-1.rds.amazonaws.com:3306'
db_name = 'fEzX33PCybDMj3eq'

# DB Instance Identifier: Bux67PTnrZAQk5qDKzaM

connection_string = 'mysql+mysqldb://{}:{}@{}/{}'.format(master_username,
                                                         password,
                                                         url, db_name)

CONFIGS['PRODUCTION'] = {
    'connection_string': connection_string,
    'secret_key': 'dQ8L%8IpZPrMmZqDpHiI',
    'host': '0.0.0.0',
    'port': 5000,
    'debug': False,
    'env': 'PRODUCTION',
    'login_captcha_secret': '6Lcjni4UAAAAAO7s-jgKUW6xr2sVfh0uvjGQKtIZ',
    'signup_captcha_secret': '6LdqpS4UAAAAAGPjpvVk6vzMAEwpiEUXR6lcjJ5X',
    'sendgrid': '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',
    'etherscan': '7CNDPRS3RPXY69937PPVRJG2WZDD9XWNQ6',
    'sendgrid_template_id': '610d1f67-aef5-479f-9544-51f5ad4f1788',
}


def get_config(env=None):
    """Respond with prod config."""
    return CONFIGS['PRODUCTION']
