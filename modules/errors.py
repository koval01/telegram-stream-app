from flask import json, render_template, request
from flask_log_request_id import current_request_id

from werkzeug.exceptions import HTTPException
from werkzeug.wrappers.response import Response

from app import app


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> Response | tuple[render_template, int]:
    """
    Handle HTTP exceptions and provide a customized error response.

    This function serves as an error handler for HTTP exceptions in the Flask application.
    It takes an HTTPException as input, generates an appropriate error response, and returns it.

    :param e: An instance of an HTTPException representing the raised exception.
    :type e: HTTPException

    :return: A Flask Response object or a tuple containing a render_template object and an HTTP status code.
    :rtype: Response | tuple[render_template, int]

    This function performs the following steps: 1. Retrieve the appropriate response for the error from the
    exception.
    2. Assigns a unique request ID to the error for tracking purposes.
    3. Check if there is a 'Referer'
    header in the request.
    4. If there is no 'Referer' header, renders an HTML error template with error details and
    returns it with the error code.
    5. If there is a 'Referer' header, replaces the response body with a JSON
    representation of the error and sets the content type to 'application/json'.
    Returns the modified response.

    Example usage: - When an HTTP exception occurs in the Flask application, this function is called to handle the
    exception and provide an appropriate error response.
    The response can either be HTML or JSON, depending on the
    request headers.

    Note: - The 'HTTPException' class is a base class for all HTTP-related exceptions in Flask, and this handler is
    designed to provide a consistent error response for all such exceptions.
    """

    # Get the appropriate response for the error
    response = e.get_response()

    e.current_request_id = current_request_id()

    if not request.headers.get('Referer'):
        return render_template("error.html", e=e), e.code

    # Replace the response body with a JSON representation of the error
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })

    # Set the content type of the response to JSON
    response.content_type = "application/json"

    return response
