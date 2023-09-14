from wsgiref.headers import Headers

from flask import Response
from flask_log_request_id import current_request_id

from app import app


@app.after_request
def append_request_id(response: Response) -> Response:
    """
    Appends the current request ID to the response headers if the app is in debug mode.

    Args:
        response (Response): The Flask response object.

    Returns:
        Response: The modified response object with the request ID header added.
    """
    if app.debug:
        response.headers.add('X-APP-REQUEST-ID', current_request_id())

    return response


@app.after_request
def headers_remove(response: Response) -> Response:
    """
    Removes specified headers from the response.

    Args:
        response (Response): The Flask response object.

    Returns:
        Response: The modified response object with specified headers removed.
    """
    headers_to_remove = ["Date", "Via", "Server"]

    for header in headers_to_remove:
        if header in response.headers:
            del response.headers[header]

    return response
