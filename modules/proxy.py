from flask import Response

from app import app
from misc.proxy import proxy


@app.route('/<path:url>', methods=['GET', 'POST'])
def proxy_method(url: str) -> Response | tuple[dict, int]:
    return proxy(url)
