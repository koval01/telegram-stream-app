from flask import Response

from app import app, limiter
from misc.proxy import proxy


@app.route('/', methods=['GET', 'POST'])
@limiter.limit("8 per minute")
def index() -> Response | tuple[dict, int]:
    return proxy(f"https://t.me/s/{app.config['CHANNEL_NAME']}", internal_call=True)


@app.route('/v/', methods=['POST'])
@limiter.limit("1 per 3 seconds")
def view_send() -> Response | tuple[dict, int]:
    return proxy("https://t.me/v", internal_call=True)


@app.route('/<int:post>', methods=['GET'])
@limiter.limit("8 per minute")
def select_post(post: int) -> Response | tuple[dict, int]:
    return proxy(f"https://t.me/s/{app.config['CHANNEL_NAME']}/{post}", internal_call=True)
