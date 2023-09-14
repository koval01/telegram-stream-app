import typing

from flask import Response

from app import app, limiter
from misc.proxy import proxy


@app.route('/', methods=['GET', 'POST'])
@limiter.limit("8 per minute")
def index() -> Response | typing.NoReturn:
    """
    Route for handling requests to the root URL '/'. It proxies requests to a Telegram channel.

    Returns:
        Response | typing.NoReturn: The response object or None.
    """
    return proxy(f"https://t.me/s/{app.config['CHANNEL_NAME']}", internal_call=True)


@app.route('/v/', methods=['POST'])
@limiter.limit("1 per 3 seconds")
def view_send() -> Response | typing.NoReturn:
    """
    Route for handling 'view send' requests. It proxies requests to the Telegram 'view send' page.

    Returns:
        Response | typing.NoReturn: The response object or None.
    """
    return proxy("https://t.me/v", internal_call=True)


@app.route('/<int:post>', methods=['GET'])
@limiter.limit("8 per minute")
def select_post(post: int) -> Response | typing.NoReturn:
    """
    Route for handling requests to view a specific post in the Telegram channel.

    Args:
        post (int): The post number to view.

    Returns:
        Response | typing.NoReturn: The response object or None.
    """
    return proxy(f"https://t.me/s/{app.config['CHANNEL_NAME']}/{post}", internal_call=True)
