# """All models related to the DApp popularity section of the site.

# Prefixed with 'List'.
# """

# from lib.models.db import Base
# from sqlalchemy import Column, DateTime, String, Integer

# import datetime
# import uuid


# class ListDapp(Base):
#     """DApps that are listed on the site."""

#     __tablename__ = 'list_dapp'
#     id = Column(String(36), primary_key=True)
#     created_at = Column(DateTime, nullable=False)
#     name = Column(String(100), nullable=False)
#     website = Column(String(100))

#     def __init__(self, name, website, id=None):
#         """Constructor."""
#         self.id = id or str(uuid.uuid4())
#         self.created_at = datetime.datetime.now()
#         self.name = name
#         self.website = website


# class ListContract(Base):
#     """Past, present and future contracts of a DApp."""

#     __tablename__ = 'list_contract'
#     # There is no need to add a synthetic primary key to this table
#     # as the contract hash does the job well enough.
#     address = Column(String(42), primary_key=True)
#     created_at = Column(DateTime, nullable=False)
#     dapp_id = Column(String(36), nullable=False)
#     state = Column(Integer, nullable=False)
#     # 0 - Unknown
#     # 1 - Active
#     # 2 - Past
#     # 3 - Future

#     def __init__(self, dapp_id, address, state=0):
#         """Constructor."""
#         self.created_at = datetime.datetime.now()
#         self.dapp_id = dapp_id
#         self.address = address
#         self.state = state


# class ListRawTransaction(Base):
#     """All transactions of relevant contracts as received from etherscan.

#     No processing has been performed on this data and it should not be
#     used directly for charting.
#     """

#     __tablename__ = 'list_raw_transaction'
#     # There is no need to add a synthetic primary key to this table
#     # as tx hash does the job well enough.
#     created_at = Column(DateTime, nullable=False)
#     hash = Column(String(66), primary_key=True)
#     contract = Column(String(42), nullable=False)
#     block_number = Column(Integer, nullable=False)
#     gas_used = Column(Integer, nullable=False)
#     gas_price = Column(Integer, nullable=False)
#     time_stamp = Column(DateTime, nullable=False)

#     def __init__(self, hash, contract, block_number,
#                  gas_used, gas_price, time_stamp):
#         """Constructor."""
#         self.created_at = datetime.datetime.now()
#         self.hash = hash
#         self.contract = contract
#         self.block_number = block_number
#         self.gas_used = gas_used
#         self.gas_price = gas_price
#         self.time_stamp = datetime.datetime.fromtimestamp(time_stamp)
