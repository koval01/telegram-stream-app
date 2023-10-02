from time import time

from flask import Response, g
from flask_log_request_id import current_request_id

from app import app


@app.before_request
def start_timer():
    """
    Record the start time of the request.

    This function is an `@app.before_request` handler, which means it is executed before each incoming request to the
    Flask application.
    Its purpose is to record the start time of the request in the `request.start_time` attribute.

    Returns:
        None
    """

    g.start_time = time()


@app.after_request
def add_processing_time(response):
    """
    Add the processing time to the response headers.

    This function is an `@app.after_request` handler,
    which means it is executed after each request to the Flask application.
    It calculates the processing time of the request in milliseconds
    and adds it to the response headers as 'X-Processing-Time'.

    Args:
        response: The Flask response object.

    Returns:
        response: The response object with processing time added to headers.
    """

    # Calculate the processing time in milliseconds
    processing_time = (time() - g.start_time) * 1000

    # Add the processing time to the response headers
    response.headers['X-Processing-Time'] = f"{processing_time:.0f} ms"

    return response


@app.after_request
def append_request_id(response: Response) -> Response:
    """
    Appends the current request ID to the response headers.

    This function is an `@app.after_request` handler, executed after each request to the Flask application.
    It adds the current request ID as 'X-App-Request-ID' to the response headers.

    Args:
        response (Response): The Flask response object.

    Returns:
        Response: The modified response object with the request ID header added.
    """

    response.headers.add('X-App-Request-ID', current_request_id())

    return response
