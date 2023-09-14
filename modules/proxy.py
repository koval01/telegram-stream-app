import typing

from flask import Response

from app import app
from misc.proxy import proxy


@app.route('/<path:url>', methods=['GET', 'POST'])
def proxy_method(url: str) -> Response | typing.NoReturn:
    """
    Route for proxying requests to a specified URL.

    Args:
        url (str): The URL to be proxied.

    Returns:
        Response | typing.NoReturn: The response object or None.
    """
    return proxy(url)
