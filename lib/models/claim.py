"""Claim models."""

from lib.models.db import Base
from sqlalchemy import Column, DateTime, String, Text

import datetime
import uuid


class Claim(Base):
    """Policy information."""

    __tablename__ = 'claim'
    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, nullable=False)

    policy_id = Column(String(36), nullable=False)
    dapp_id = Column(String(36), nullable=False)
    message = Column(Text, nullable=False)
    insuree_signature = Column(String(132), nullable=False)
    insuree_address = Column(String(42), nullable=False)
    user_id = Column(String(36), nullable=False)
    claim_remark = Column(String(36), nullable=False)

    status = Column(String(100), nullable=False)
    insurer_signature = Column(String(132))
    claim_settlement_time = Column(DateTime)
    note = Column(Text)

    def __init__(self, policy_id, dapp_id, message, insuree_signature,
                 insuree_address, user_id, claim_remark,
                 status='Submitted', insurer_signature=''):
        """Constructor."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.policy_id = policy_id
        self.dapp_id = dapp_id

        self.message = message
        self.insuree_signature = insuree_signature
        self.insuree_address = insuree_address
        self.user_id = user_id
        self.claim_remark = claim_remark
        self.status = status
        self.insurer_signature = insurer_signature
        self.note = ''
