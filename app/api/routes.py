from datetime import timezone
from uuid import UUID

import pydantic
from pydantic.datetime_parse import parse_datetime
from aiohttp import web
from aiohttp.web_request import Request
from api import crud, schemas


async def create_user(request: Request):
    body_json = await request.json()
    try:
        user_schema = schemas.UserIn(**body_json)
    except pydantic.ValidationError as e:
        return web.Response(body=e.json(), status=400, content_type='application/json')
    id, name = await crud.create_user(user_schema)
    return web.json_response({
        'id': id,
        'name': name,
    })


async def get_user(request: Request):
    try:
        user_id = int(request.match_info['id'])
    except ValueError:
        return web.Response(
            body='{"message": "Please provide number user id"}',
            status=400,
            content_type='application/json'
        )
    date = request.rel_url.query.get('date', None)
    try:
        if date:
            dt = parse_datetime(date)
            # By defaults pydantic converts time to local timezone if there were
            # no info about TZ, but we asserts it in UTC
            dt = dt.replace(tzinfo=None)
            id, name, balance, dt = await crud.get_history_user_balance(user_id, dt)
        else:
            id, name, balance, dt = await crud.get_user_balance_current(user_id)
    except crud.NotFoundError:
        return web.Response(
            body='{"message": "User not found"}',
            status=404,
            content_type='application/json'
        )
    except crud.NoBalanceInfo:
        return web.Response(
            body='{"message": "No balance info for this datetime"}',
            status=400,
            content_type='application/json'
        )
    return web.json_response({
        'id': id,
        'name': name,
        'balance': balance,
        'datetime': dt.isoformat(),
    })


async def add_transaction(request: Request):
    body_json = await request.json()
    try:
        transaction_schema = schemas.TransactionIn(**body_json)
    except pydantic.ValidationError as e:
        return web.Response(body=e.json(), status=400, content_type='application/json')
    print(transaction_schema)

    try:
        await crud.add_transaction(transaction_schema)
    except crud.NotFoundError:
        return web.Response(
            body='{"message": "User not found"}',
            status=404,
            content_type='application/json'
        )
    except crud.TransactionAlreadyExistsError:
        return web.Response(
            body='{"message": "Transaction already exists"}',
            status=400,
            content_type='application/json'
        )
    return web.Response(status=200)


async def get_transaction(request: Request):
    try:
        transaction_uuid = UUID(request.match_info['id'])
    except ValueError:
        return web.Response(
            body='{"message": "Please provide valid transaction UUID"}',
            status=400,
            content_type='application/json'
        )
    try:
        transaction = await crud.get_transaction(str(transaction_uuid))
    except crud.NotFoundError:
        return web.Response(
            body='{"message": "Transaction not found"}',
            status=404,
            content_type='application/json'
        )
    return web.json_response({
        'uuid': transaction.uuid,
        'user_id': transaction.user_id,
        'type': 'DEPOSIT' if transaction.type == 1 else 'WITHDRAW',
        'amount': f'{transaction.amount/100:.2f}',
        'datetime': transaction.datetime.replace(tzinfo=timezone.utc).isoformat(),
    })


def add_routes(app):
    app.router.add_route('POST', r'/v1/user', create_user, name='create_user')
    app.router.add_route('GET', r'/v1/user/{id}', get_user, name='get_user')
    app.router.add_route('POST', r'/v1/transaction', add_transaction, name='add_transaction')
    app.router.add_route('GET', r'/v1/transaction/{id}', get_transaction, name='incoming_transaction')
