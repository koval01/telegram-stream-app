from app import app

from flask import json

from werkzeug.wrappers.response import Response
from werkzeug.exceptions import HTTPException


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> Response:
    """
    Custom error handler for handling HTTP exceptions and returning JSON responses.

    Args:
        e (HTTPException): The HTTP exception to handle.

    Returns:
        Response: A JSON response containing error code, name, and description.
    """
    # TODO: If the request does not have a Referer header,
    #  then you need to give a custom error page, that is, render html

    # Get the appropriate response for the error
    response = e.get_response()

    # Replace the response body with a JSON representation of the error
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })

    # Set the content type of the response to JSON
    response.content_type = "application/json"

    return response
