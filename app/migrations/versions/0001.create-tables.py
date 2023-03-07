from yoyo import step

print('0001.create-tables.py: creating tables if not exists...')
steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL primary key,
            name varchar(30) not null,
            balance int DEFAULT 0
        )"""
    ),
    step(
        """
        CREATE TABLE transactions_types (
            id smallint primary key,
            name VARCHAR not null
        )"""
    ),
    step(
        """
        INSERT INTO transactions_types VALUES
            (0, 'unknown'),
            (1, 'DEPOSIT'),
            (2, 'WITHDRAW')
        """
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            uuid uuid primary key,
            user_id int,
            type SMALLINT not null,
            amount int not null,
            post_transaction_balance int not null,
            datetime timestamp not null,
            CONSTRAINT fk_user
                FOREIGN KEY(user_id)
                    REFERENCES users(id),
            CONSTRAINT fk_type
                FOREIGN KEY(type)
                    REFERENCES transactions_types(id)
        )"""
    ),
]
