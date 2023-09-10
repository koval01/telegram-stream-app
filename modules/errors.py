from flask import render_template

from app import app


# Define Error handler for 400
@app.errorhandler(400)
def error_400(e: str | None) -> tuple[dict, int]:
    return {"code": 400, "message": "bad request"}, 400


# Define Error handler for 404
@app.errorhandler(404)
def error_404(e: str | None) -> tuple[render_template, int]:
    return render_template('nothing.html'), 404


# Define Error handler for 403
@app.errorhandler(403)
def error_403(e: str | None) -> tuple[dict, int]:
    return {"code": 403, "message": "forbidden"}, 403


# Define Error handler for 405
@app.errorhandler(405)
def error_405(e: str | None) -> tuple[dict, int]:
    return {"code": 405, "message": "method not allowed"}, 405


# Define Error handler for 408
@app.errorhandler(408)
def error_408(e: str | None) -> tuple[dict, int]:
    return {"code": 408, "message": "your request is taking too long to be served"}, 408


# Define Error handler for 418
@app.errorhandler(418)
def error_418(e: str | None) -> tuple[dict, int]:
    return {"code": 418, "message": "Yes, I am a Teapot"}, 418


# Define Error handler for 429
@app.errorhandler(429)
def error_429(e: str | None) -> tuple[dict, int]:
    return {"code": 429, "message": "Too Many Requests"}, 429
