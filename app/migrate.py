from yoyo import read_migrations
from yoyo import get_backend
from config import Config

if __name__ == '__main__':
    print('Executing migrations...')

    backend = get_backend(
        f'postgres://{Config.DATABASE_USER}:{Config.DATABASE_PASSWORD}@{Config.DATABASE_HOST}:{Config.DATABASE_PORT}/{Config.DATABASE_NAME}'
    )
    migrations = read_migrations('migrations/versions')

    with backend.lock():

        # Apply any outstanding migrations
        backend.apply_migrations(backend.to_apply(migrations))

        # Rollback all migrations
        # backend.rollback_migrations(backend.to_rollback(migrations))

    print('Done!')
