from flask import render_template

from app import app


from flask import json
from werkzeug.wrappers.response import Response
from werkzeug.exceptions import HTTPException


@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException) -> Response:
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response
