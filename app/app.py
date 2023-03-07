from aiohttp import web
from api.routes import add_routes
from config import Config


app = web.Application()


def init_app() -> web.Application:
    app['config'] = Config
    add_routes(app)
    return app
