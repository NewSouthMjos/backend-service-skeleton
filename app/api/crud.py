from datetime import datetime, timezone

import models
from api import schemas
from database import AsyncSessionLocal
from sqlalchemy import insert, select, update, func, desc
from sqlalchemy.exc import IntegrityError


class NotFoundError(Exception):
    pass


class TransactionAlreadyExistsError(Exception):
    pass


class NoBalanceInfo(Exception):
    pass


class NotEnoughMoneyError(Exception):
    pass


async def create_user(user_schema: schemas.UserIn):
    async with AsyncSessionLocal() as db_session:
        q = insert(models.User)\
            .values(name=user_schema.name,)\
            .returning(models.User.id, models.User.name)
        result = (await db_session.execute(q)).first()
        await db_session.commit()
    id, name = result[0], result[1]
    return id, name


async def get_user_balance_current(id: str):
    async with AsyncSessionLocal() as db_session:
        q = select(models.User)\
            .where(models.User.id == id)
        result = (await db_session.execute(q)).scalars().first()
    if not result:
        raise NotFoundError
    dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    balance_str = f'{result.balance/100:.2f}'
    return result.id, result.name, balance_str, dt


async def add_transaction(transaction_schema: schemas.TransactionIn):
    async with AsyncSessionLocal() as db_session:
        q = select(models.User.balance)\
            .where(models.User.id == transaction_schema.user_id)
        current_user_balance = (await db_session.execute(q)).scalars().first()
        if current_user_balance is None:
            raise NotFoundError
        
        if transaction_schema.type == 1:
            new_user_balance = current_user_balance + int(transaction_schema.amount*100)
        else:  # type == 2
            new_user_balance = current_user_balance - int(transaction_schema.amount*100)
        if new_user_balance < 0:
            raise NotEnoughMoneyError
        q = insert(models.Transaction)\
            .values(
                uuid=str(transaction_schema.uid),
                user_id=transaction_schema.user_id,
                type=transaction_schema.type,
                amount=int(transaction_schema.amount*100),
                post_transaction_balance=new_user_balance,
                datetime=transaction_schema.timestamp,
            )
        try:
            await db_session.execute(q)
        except IntegrityError:
            raise TransactionAlreadyExistsError

        q = update(models.User)\
            .where(models.User.id == transaction_schema.user_id)\
            .values(balance=new_user_balance)
        await db_session.execute(q)
        await db_session.commit()


async def get_transaction(uuid: str):
    async with AsyncSessionLocal() as db_session:
        q = select(models.Transaction)\
            .where(models.Transaction.uuid == uuid)
        result = (await db_session.execute(q)).scalars().first()
    if not result:
        raise NotFoundError
    return result


async def get_history_user_balance(id: str, dt: datetime):
    async with AsyncSessionLocal() as db_session:
        q = select(models.User)\
            .where(models.User.id == id)
        result = (await db_session.execute(q)).scalars().first()
        if not result:
            raise NotFoundError

        q = select(models.Transaction.post_transaction_balance)\
            .where(models.Transaction.user_id == id)\
            .where(models.Transaction.datetime < dt)\
            .order_by(desc(models.Transaction.datetime))

        balance = (await db_session.execute(q)).scalars().first()
        if balance is None:
            raise NoBalanceInfo
        balance_str = f'{balance/100:.2f}'
    return result.id, result.name, balance_str, dt
