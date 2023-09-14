import typing

from flask import Response

from app import app, limiter
from misc.proxy import proxy


@app.route('/', methods=['GET', 'POST'])
@limiter.limit("8 per minute")
def index() -> Response | typing.NoReturn:
    """
    Route for handling requests to the root URL '/'.
    Its proxies request to a Telegram channel.

    Returns:
        Response | typing.NoReturn: The response object or None.
    """
    return proxy(f"https://t.me/s/{app.config['CHANNEL_NAME']}", internal_call=True)


@app.route('/v/', methods=['POST'])
@limiter.limit("1 per 2 seconds")
def view_send() -> Response | typing.NoReturn:
    """
    Route for handling 'view sends' requests.
    Its proxies requests to the Telegram 'view send' page.

    Returns:
        Response | typing.NoReturn: The response object or None.
    """
    return proxy("https://t.me/v/", internal_call=True)


@app.route('/i/<path:path>', methods=['GET'])
@limiter.limit("30 per minute")
def i_path(path: str) -> Response | typing.NoReturn:
    """
    Route for processing requests from the t.me host with a path starting with "/i/"

    Returns:
        Response | typing.NoReturn: The response object or None.
    """
    return proxy(f"https://t.me/i/{path}", internal_call=True)


@app.route('/js/<path:path>', methods=['GET'])
@limiter.limit("30 per minute")
def js_path(path: str) -> Response | typing.NoReturn:
    """
    Route for processing requests from the t.me host with a path starting with "/js/"

    Returns:
        Response | typing.NoReturn: The response object or None.
    """
    return proxy(f"https://t.me/js/{path}", internal_call=True)


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
