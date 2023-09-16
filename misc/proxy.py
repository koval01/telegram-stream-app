import typing
import sentry_sdk
from urllib.parse import urlparse

import requests
import validators
from flask import Response, abort

from misc.bs4_methods import *
from misc.regex import *


def __style(res: requests.Response) -> bytes | str:
    """
    Style the response content based on Content-Type.

    Args:
        res (requests.Response): The HTTP response.

    Returns:
        bytes | str: The styled content.
    """
    if "Content-Type" not in res.headers.keys():
        return res.content

    c_type = res.headers.get("Content-Type").split(";")[0]
    position = request.args.get("before") or request.args.get("after")

    if (c_type in ("text/html", "text/css", "application/json",)) or position:
        body = res.text

        if c_type == "text/css":
            # replace css from another source
            body = re.sub(r"'(\.\.)(/fonts/.*?)'", font_link_update, body)

        elif (c_type == "application/json") and (not position):
            body = process_json(body)

        elif c_type == "text/html":
            # Apply custom CSS and manipulate the HTML content
            body = add_custom_css(body)
            body = update_meta_tags(body)
            body = set_bg_canvas_colors(body)
            body = remove_by_cls(body, [
                'tgme_widget_message_bubble_tail',
                'tgme_widget_message_user',
                'tgme_header_right_column'
            ])

        elif position:
            # Manipulate JSON response
            body = json.loads(body)
            body = remove_by_cls(body, [
                'tgme_widget_message_bubble_tail',
                'tgme_widget_message_user'
            ])
            body = json.dumps(body)

        return body

    return res.content


def proxy(url: str, internal_call: bool = False) -> Response | typing.NoReturn:
    """
    Proxy a URL request with optional internal call.

    Args:
        url (str): The URL to proxy.
        internal_call (bool, optional): Whether it's an internal call. Defaults to False.

    Returns:
        Response | typing.NoReturn: The proxied response or an error response.
    """
    url = f"https://{url}"

    if not validators.url(url, may_have_port=False):
        return abort(400, f"Invalid URL. URL: {url}")

    allowed_hosts = ['telegram.org', 'cdn4.telegram-cdn.org']

    if internal_call:
        allowed_hosts.append('t.me')

    host = urlparse(url).netloc.split(":")[0]
    if host not in allowed_hosts:
        return abort(403, f"Host {host} is not allowed")

    try:
        headers = {
            k: v
            for k, v in request.headers
            if k.lower() != 'host'
        }

        res = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = {
            k: process_location_header(v) if k.lower() == "location" else v
            for k, v in res.raw.headers.items()
            if k.lower() not in excluded_headers
        }

        body = __style(res)
        content_type = headers.get('Content-Type').split(';')[0]

        position = request.args.get("before") or request.args.get("after")

        if (isinstance(body, str) and (content_type == "text/html")) or position:
            body = replace_origin_host(body)

        response = Response(body, res.status_code, headers)
        return response

    except requests.exceptions.RequestException as e:
        return abort(503, str(e) if app.debug else 'hidden')

    except Exception as e:
        sentry_sdk.capture_exception(e)
        return abort(500, str(e) if app.debug else 'hidden')
