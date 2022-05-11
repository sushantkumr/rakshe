"""All models related to policies."""

from lib.models.db import Base
from sqlalchemy import (Boolean, Integer, Column,
                        DateTime, String, Text, Numeric)

import datetime
import json
import uuid


class Dapp(Base):
    """DApps that are or were being insured."""

    __tablename__ = 'dapp'

    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, nullable=False)
    name = Column(String(100), nullable=False)
    website = Column(String(100))
    approved = Column(Boolean, nullable=False)
    total_coverage_limit = Column(Numeric(18, 8, asdecimal=False), nullable=False)
    total_issued = Column(Numeric(18, 8, asdecimal=False), nullable=False)
    policy_coverage_max = Column(Numeric(18, 8, asdecimal=False), nullable=False)
    policy_coverage_min = Column(Numeric(18, 8, asdecimal=False), nullable=False)

    def __init__(self, name, website, id=None, approved=False,
                 total_coverage_limit=0, policy_coverage_max=0,
                 policy_coverage_min=0, total_issued=0):
        """Constructor."""
        self.id = id or str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.name = name
        self.website = website
        self.approved = approved
        self.total_coverage_limit = total_coverage_limit
        self.policy_coverage_max = policy_coverage_max
        self.policy_coverage_min = policy_coverage_min
        self.total_issued = total_issued


class Contract(Base):
    """Past, present and future contracts of a DApp."""

    __tablename__ = 'contract'
    id = Column(String(36), primary_key=True)
    address = Column(String(42))
    github_source = Column(Text)
    created_at = Column(DateTime, nullable=False)
    dapp_id = Column(String(36), nullable=False)
    state = Column(Integer, nullable=False)
    # 0 - Unknown
    # 1 - Active
    # 2 - Past
    # 3 - Future

    def __init__(self, dapp_id, address='', github_source='', state=0):
        """Constructor."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.dapp_id = dapp_id
        self.address = address
        self.github_source = github_source
        self.state = state


class Policy(Base):
    """Policy information."""

    __tablename__ = 'policy'
    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, nullable=False)

    dapp_id = Column(String(36), nullable=False)
    contracts = Column(Text, nullable=False)
    message = Column(Text, nullable=False)
    insuree_signature = Column(String(132), nullable=False)
    insuree_address = Column(String(42), nullable=False)
    user_id = Column(String(36), nullable=False)

    status = Column(String(100), nullable=False)
    insurer_address = Column(String(42))
    insurer_signature = Column(String(132))
    policy_activation_time = Column(DateTime)
    policy_termination_time = Column(DateTime)
    note = Column(Text)

    coverage_limit = Column(Numeric(18, 8, asdecimal=False), nullable=False)
    fee = Column(Numeric(18, 8, asdecimal=False), nullable=False)
    fee_received = Column(Boolean, nullable=False, default=False)
    tx_hash = Column(String(66))

    def __init__(self, dapp_id, contracts, message, insuree_signature,
                 insuree_address, user_id, coverage_limit, fee,
                 fee_received=False, status='Submitted', insurer_signature=''):
        """Constructor."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.dapp_id = dapp_id

        if type(contracts) != 'str':
            contracts = json.dumps(contracts)

        self.contracts = contracts
        self.message = message
        self.insuree_signature = insuree_signature
        self.insuree_address = insuree_address
        self.user_id = user_id
        self.status = status
        self.note = ''

        self.coverage_limit = coverage_limit
        self.fee = fee
        self.fee_received = fee_received
