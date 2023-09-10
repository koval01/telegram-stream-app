from flask import request, Response
from urllib.parse import urlparse
from app import app
import requests
import validators
from misc.bs4_methods import *
from misc.regex import *
from misc.crypt import Crypt


def __style(res: requests.Response) -> bytes | str:
    if "Content-Type" not in res.headers.keys():
        return res.content

    c_type = res.headers.get("Content-Type").split(";")[0].strip()

    if c_type != "text/html":
        return res.content

    body = res.text

    body = add_custom_css(body)
    body = set_bg_canvas_colors(body)
    body = remove_by_cls(body, [
        'tgme_widget_message_bubble_tail',
        'tgme_widget_message_user',
        'tgme_header_right_column'
    ])

    return body


def proxy(url, internal_call: bool = False) -> Response | tuple[dict, int]:
    try:
        url = Crypt().dec(url.split(".")[0]) if not internal_call else url
    except Exception as e:
        return {"code": 500, "message": f"Input invalid. Exception: {str(e) if app.debug else 'hidden'}"}, 500

    if not validators.url(url, may_have_port=False):
        return {"code": 400, "message": "invalid url"}, 400

    allowed_hosts = ['telegram.org', 'cdn4.telegram-cdn.org']

    if internal_call:
        allowed_hosts.append('t.me')

    host = urlparse(url).netloc.split(":")[0]
    if host not in allowed_hosts:
        return {"code": 403, "message": f"host {host} is not allowed"}, 403

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
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = {
            k: process_location_header(v, request) if k.lower() == "location" else v
            for k, v in res.raw.headers.items()
            if k.lower() not in excluded_headers
        }

        body = __style(res)

        if type(body) is str:
            body = replace_origin_host(body, request)

        response = Response(body, res.status_code, headers)
        return response

    except requests.exceptions.RequestException as e:
        return {"code": 503, "message": str(e) if app.debug else 'hidden'}, 503

    except Exception as e:
        return {"code": 500, "message": str(e) if app.debug else 'hidden'}, 500
