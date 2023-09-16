from app import app

from flask import json, render_template, request
from flask_log_request_id import current_request_id

from werkzeug.wrappers.response import Response
from werkzeug.exceptions import HTTPException


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> Response | tuple[render_template, int]:
    """
    Custom error handler for handling HTTP exceptions and returning JSON responses.

    Args:
        e (HTTPException): The HTTP exception to handle.

    Returns:
        Response: A JSON response containing error code, name, and description.
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
