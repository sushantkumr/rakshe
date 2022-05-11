from lib.models.db import Base
from sqlalchemy import Column, DateTime, String

import datetime
import uuid


class AuditApplication(Base):
    __tablename__ = 'audit_application'
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36))
    created_at = Column(DateTime)
    name = Column(String(100))
    source_code_link = Column(String(100))
    dapp_website = Column(String(100))
    dapp_description = Column(String(1000))
    status = Column(String(100))

    def __init__(self, user_id, name, source_code_link,
                 dapp_website, dapp_description, status):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.created_at = datetime.datetime.now()
        self.name = name
        self.source_code_link = source_code_link
        self.dapp_website = dapp_website
        self.dapp_description = dapp_description
        self.status = status
