from wsgiref.headers import Headers

from flask import Response, request
from flask_log_request_id import current_request_id

from app import app

from time import time


@app.before_request
def start_timer():
    """
    Record the start time of the request.
    """
    request.start_time = time()


@app.after_request
def add_processing_time(response):
    """
    Add the processing time to the response headers.

    Args:
        response: The Flask response object.

    Returns:
        response: The response object with processing time added to headers.
    """
    # Calculate the processing time in milliseconds
    processing_time = (time() - request.start_time) * 1000

    # Add the processing time to the response headers
    response.headers['X-Processing-Time'] = f"{processing_time:.0f} ms"

    return response


@app.after_request
def append_request_id(response: Response) -> Response:
    """
    Appends the current request ID to the response headers.

    Args:
        response (Response): The Flask response object.

    Returns:
        Response: The modified response object with the request ID header added.
    """
    response.headers.add('X-App-Request-ID', current_request_id())

    return response


@app.after_request
def channel_name(response: Response) -> Response:
    """
    Add the Telegram channel name to the response headers.

    Args:
        response (Response): The Flask response object.

    Returns:
        Response: The response object with the 'TG-Channel-Name' header added.
    """
    response.headers.add('TG-Channel-Name', app.config["CHANNEL_NAME"])
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
