from wsgiref.headers import Headers

from flask import Response
from flask_log_request_id import current_request_id

from app import app


@app.after_request
def append_request_id(response: Response) -> Response:
    response.headers.add(
        'X-APP-REQUEST-ID',
        current_request_id()
    ) if app.debug else None

    return response


@app.after_request
def headers_remove(response: Response) -> Response:
    headers_to_remove = ["Date", "Via", "Server"]

    for header in headers_to_remove:
        if header in response.headers:
            del response.headers[header]

    return response
