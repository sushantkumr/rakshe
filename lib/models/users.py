from lib.models.db import Base
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, String

import datetime
import uuid
from lib.models import utils


class User(UserMixin, Base):
    __tablename__ = 'user'
    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime)
    name = Column(String(100))
    salt = Column(String(29))
    hash = Column(String(60))
    is_admin = Column(Boolean)
    email = Column(String(100))
    email_verified = Column(Boolean)

    def __init__(self, password, name, is_admin=False, email=''):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.name = name
        self.salt, self.hash = utils.hash_password(password)
        self.is_admin = is_admin
        self.email = email
        self.email_verified = False

    def __repr__(self):
        return '<User %r>' % (self.name)


class JoinUs(Base):
    __tablename__ = 'joinus'
    id = Column(String(36), primary_key=True)
    created_at = Column(DateTime)
    insuree = Column(Boolean)
    bounty_hunter = Column(Boolean)
    auditor = Column(Boolean)
    agent = Column(Boolean)
    developer = Column(Boolean)
    email = Column(String(100))

    def __init__(self, insuree, bounty_hunter, auditor, agent, developer, email):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.datetime.now()
        self.insuree = insuree
        self.bounty_hunter = bounty_hunter
        self.auditor = auditor
        self.agent = agent
        self.developer = developer
        self.email = email


class Token(Base):
    __tablename__ = 'token'
    created_at = Column(DateTime)
    hash = Column(String(100), primary_key=True)
    salt = Column(String(100))
    user_id = Column(String(36))
    used = Column(Boolean)
    flag = Column(String(100))

    def __init__(self, hash, salt, user_id, flag, used=False):
        self.created_at = datetime.datetime.now()
        self.hash = hash
        self.salt = salt
        self.used = used
        self.flag = flag
        self.user_id = user_id
