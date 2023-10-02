import typing

from flask import Response

from app import app, limiter
from misc.proxy import Proxy


@app.route('/<path:url>', methods=['GET', 'POST'])
@limiter.limit("250 per minute")
def proxy_method(url: str) -> Response | typing.NoReturn:
    """
    Route for proxying requests to a specified URL.

    This function is used as a route handler for proxying requests to a specified URL.
    It handles both GET and POST requests and takes the 'url' parameter, which is the URL to be proxied.

    Args:
        url (str): The URL to be proxied.

    Returns:
        Response | typing.NoReturn: The response object or None.

    Example usage:
    - A GET or POST request to '/some_url' will proxy the request to 'some_url' and return the response.
    Examples: /cdn4.telegram.net/path/file.ext or /t.me/api_endpoint
    """

    return Proxy(url).make_request()
