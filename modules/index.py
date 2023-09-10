from app import app
from misc.proxy import proxy
from flask import Response


@app.route('/')
def index() -> Response | tuple[dict, int]:
    return proxy("https://t.me/s/telelug", internal_call=True)
