from flask import Response
from misc.proxy import proxy
from app import app


@app.route('/<path:url>', methods=['GET', 'POST'])
def proxy_method(url) -> Response | tuple[dict, int]:
    return proxy(url)
