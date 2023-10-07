import typing

from flask import Response, request, redirect, url_for, g

from app import app, limiter
from misc.proxy import Proxy


@app.route("/healthz", methods=["GET", "HEAD"])
def healthz() -> str:
    """
    Endpoint for health checks (healthz).

    This Flask route handles health checks at the "/healthz" endpoint. The route only supports the GET method.

    Returns:
        Response: An empty string response. The response is used to indicate the health status of the application during
        health checks.
    """

    return ""


@app.route('/favicon.ico', methods=['GET'])
def favicon() -> Response:
    """
    Route for serving the favicon.

    This function is used to serve the favicon.ico file for a web application.
    It handles GET requests to '/favicon.ico'.
    The function redirects the request to the 'static' route with the filename 'images/favicon.ico'.

    Returns:
        Response: A Flask Response object that redirects the request to the favicon.ico file in the 'static' folder.

    Example usage:
    - A GET request to '/favicon.ico' will be redirected to the favicon.ico file located in the 'static' folder.
    """

    return redirect(url_for('static', filename='images/favicon.ico'))


@app.route('/v/', methods=['POST'])
@limiter.limit("1 per 3 seconds")
def view_send() -> Response | typing.NoReturn:
    """
    Proxy a POST request to send data to an external view endpoint.

    This function is used as a route handler for sending data to an external view endpoint,
    typically on the Telegram CDN.
    It handles POST requests sent to the '/v/' route.

    :return: A Flask Response object containing the proxied response from the external view endpoint.
    :rtype: Response

    :raises: RateLimitExceeded if the rate limit imposed by the 'limiter.limit' decorator is exceeded.

    This function is decorated with the following route pattern:
    - '/v/' for handling POST requests.

    It is also rate-limited to allow only 1 request every 3 seconds using the 'limiter.limit' decorator.

    Example usage:
    - A POST request to '/v/' will proxy the request to 'https://t.me/v/' and return the response.
    """

    return Proxy("t.me/v/", internal_call=True).make_request()


@app.route('/i/<path:path>', methods=['GET'])
@app.route('/js/<path:path>', methods=['GET'])
@limiter.limit("150 per minute")
def proxy_static(path: str) -> Response | typing.NoReturn:
    """
    Proxy static files from external sources to the current server.

    This function is used as a route handler for serving static files from external sources, such as the Telegram CDN.
    It takes a 'path' parameter, which is the path to the desired resource on the external server.

    :param path: A string representing the path to the desired resource on the external server.
    :type path: Str

    :return: A Flask Response object containing the proxied content from the external server.
    :rtype: Response

    :raises: RateLimitExceeded if the rate limit imposed by the 'limiter.limit' decorator is exceeded.

    This function is decorated with the following route patterns:
    - '/i/<path:path>' and '/js/<path:path>' for handling requests with different prefixes ('/i/' or '/js/').
    - It is also rate-limited to 150 requests per minute using the 'limiter.limit' decorator.

    Example usage:
    - If the route is accessed with '/i/some_image.png', it will proxy 'https://t.me/i/some_image.png'.
    - If the route is accessed with '/js/some_script.js', it will proxy 'https://t.me/js/some_script.js'.
    """

    return Proxy(f"t.me/{'i' if request.path.startswith('/i/') else 'js'}/{path}", internal_call=True).make_request()


@app.route(f'/{app.config["PROXY_PATH"]}/<path:url>', methods=['GET', 'POST'])
@limiter.limit("250 per minute")
def proxy_method(url: str) -> Response | typing.NoReturn:
    """
    Route for proxying requests to a specified URL.

    This function is used as a route handler for proxying requests to a specified URL.
    It handles both GET and POST requests and takes the 'url' parameter, which is the URL to be proxied.

    Args:
        url (str): The URL to be proxied.

    Returns:
        Response | typing.NoReturn: The response object or None.

    Example usage:
    - A GET or POST request to '/proxy_route/some_url' will proxy the request to 'some_url' and return the response.
    Examples: /proxy_route/cdn4.telegram.net/path/file.ext or /proxy_route/t.me/api_endpoint
    """

    return Proxy(url).make_request()


@app.route('/<path:channel>/<int:post>', methods=['GET', 'POST'])
@app.route('/<path:channel>', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def index(channel: str, post: int | None = None) -> Response | typing.NoReturn:
    """
    Proxy requests to an external channel feed.

    This function serves as a route handler for proxying requests to an external channel feed, typically on the
    Telegram CDN.
    It can handle both GET and POST requests to the root route ('/') and routes with an integer 'post'
    parameter.

    :param channel: Channel username.
    :param post: An optional integer representing the post-ID.
    If provided, the function will proxy to a specific post.
                 If not provided (defaulting to None), the function will proxy to the channel's root feed.
    :type post: Int | None

    :return: A Flask Response object containing the proxied content from the external channel feed.
    :rtype: Response

    :raises: RateLimitExceeded if the rate limit imposed by the 'limiter.limit' decorator is exceeded.

    This function is decorated with the following route patterns:
    - '/<str:channel>' for handling both GET and POST requests to the root route.
    - '/<str:channel>/<int:post>' for handling both GET and POST requests with an integer 'post' parameter.

    It is also rate-limited to allow only 15 requests per minute using the 'limiter.limit' decorator.

    Example usage:
    - A GET or POST request to '/durov' will proxy the channel's root feed.
    - A GET or POST request to '/durov/123' will proxy to the specific post with ID 123.
    """

    # set global flask var
    g.channel_name = channel

    return Proxy(f"t.me/s/{channel}/{post if post else ''}", internal_call=True).make_request()
