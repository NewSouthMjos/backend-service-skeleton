from os import getenv


class Config:
    DEBUG = str(getenv('DEBUG'))
    HOST = str(getenv('HOST'))
    PORT = str(getenv('PORT'))

    DATABASE_USER = str(getenv('DATABASE_USER'))
    DATABASE_PASSWORD = str(getenv('DATABASE_PASSWORD'))
    DATABASE_NAME = str(getenv('DATABASE_NAME'))
    DATABASE_PORT = str(getenv('DATABASE_PORT'))
    DATABASE_HOST = str(getenv('DATABASE_HOST'))
    DATABASE_URI = (
        f'postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@'\
        f'{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
    )
