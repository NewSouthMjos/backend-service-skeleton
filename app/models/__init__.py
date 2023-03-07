from sqlalchemy import (Column, DateTime, ForeignKey, Integer, SmallInteger,
                        String)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(30), nullable=False)
    balance = Column(Integer, default=0)


class TransactionType(Base):
    __tablename__ = 'transactions_types'

    id = Column(SmallInteger, primary_key=True, nullable=False)
    name = Column(String, nullable=False)


class Transaction(Base):
    __tablename__ = 'transactions'

    uuid = Column(UUID, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(SmallInteger, ForeignKey("transactions_types.id"))
    amount = Column(Integer, nullable=False)
    post_transaction_balance = Column(Integer, nullable=False)
    datetime = Column(DateTime(False), nullable=False)
