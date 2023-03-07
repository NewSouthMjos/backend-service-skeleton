import os
import uuid
from datetime import datetime
from time import sleep

import requests

HOST, PORT = os.getenv('HOST'), os.getenv('PORT')


def assert_balance(user, expected_balance, date=None):
    url = f'http://{HOST}:{PORT}/v1/user/{user["id"]}'
    if date:
        url += f'?date={date}'
    balance_resp = requests.get(url)
    assert balance_resp.status_code == 200
    assert balance_resp.json()['balance'] == expected_balance


def test_api():
    user_resp = requests.post(f'http://{HOST}:{PORT}/v1/user', json={
        'name': 'petya'
    })

    assert user_resp.status_code == 201
    user = user_resp.json()
    assert user['id'] > 0
    assert user['name'] == 'petya'

    assert_balance(user, '0.00')

    txn = {
        'uid': str(uuid.uuid4()),
        'user_id': user['id'],  # We need to specify user
        'type': 'DEPOSIT',
        'amount': '100.0',
        'timestamp': datetime(2023, 1, 4).isoformat(),  # technical field to make tests possible
    }
    txn_resp = requests.post(f'http://{HOST}:{PORT}/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, '100.00')

    detail_resp = requests.get(f'http://{HOST}:{PORT}/v1/transaction/{txn["uid"]}')
    assert detail_resp.json()['type'] == 'DEPOSIT'
    assert detail_resp.json()['amount'] == '100.00'

    txn = {
        'uid': str(uuid.uuid4()),
        'user_id': user['id'],  # We need to specify user
        'type': 'WITHDRAW',
        'amount': '50.0',
        'timestamp': datetime(2023, 1, 5).isoformat(),  # technical field to make tests possible
    }
    
    # Второй запрос с таким же UUID не должен выдвать статус 200, так как
    # должен вызывать ошибку. Поэтому проверяем правильность исполнения только
    # первого запроса
    txn_resp = requests.post(f'http://{HOST}:{PORT}/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    txn_resp = requests.post(f'http://{HOST}:{PORT}/v1/transaction', json=txn)
    assert_balance(user, '50.00')


    txn = {
        'uid': str(uuid.uuid4()),
        'user_id': user['id'],  # We need to specify user
        'type': 'WITHDRAW',
        'amount': '60.0',
        'timestamp': datetime.utcnow().isoformat(),  # technical field to make tests possible
    }
    txn_resp = requests.post(f'http://{HOST}:{PORT}/v1/transaction', json=txn)  # Ошибка? У нас нет точки v1/withdraw
    assert txn_resp.status_code == 402  # insufficient funds
    assert_balance(user, '50.00')

    txn = {
        'uid': str(uuid.uuid4()),
        'user_id': user['id'],  # We need to specify user
        'type': 'WITHDRAW',
        'amount': '10.0',
        'timestamp': datetime(2023, 2, 5).isoformat(),  # technical field to make tests possible
    }
    txn_resp = requests.post(f'http://{HOST}:{PORT}/v1/transaction', json=txn)
    assert txn_resp.status_code == 200
    assert_balance(user, '40.00')

    assert_balance(user, '50.00', date='2023-01-30T00:00:00.00000000')


if __name__ == "__main__":
    sleep(5)  # Легкое решение, чтобы быть уверенным, что контейнер payment_service запустился
    print('Running tests...')
    test_api()
    print('All tests has been passed')
