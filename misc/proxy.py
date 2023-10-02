import typing
from typing import Any
from urllib.parse import urlparse

import json
import requests
import sentry_sdk
import validators

from flask import Response, abort, request

from app import app

from misc.bs4_methods import Bs4Updater
from misc.regex import MiscRegex


class Proxy:
    """
    A class for proxying HTTP requests with optional internal call handling.

    This class provides methods for validating and making HTTP requests to the specified URL.
    It allows for proxying requests with optional content styling based on the Content-Type.

    Args:
        url (str): The URL to proxy.
        internal_call (bool, optional): Whether it's an internal call. Defaults to False.

    Attributes:
        url (str): The URL to proxy.
        internal_call (bool): Whether it's an internal call.
        allowed_hosts (list): A list of allowed hostnames for validation.

    Methods:
        make_request(): Proxy an HTTP request and return the proxied response.
        _request_validate(): Validate the URL and host based on allowed hosts.

    Static Methods:
        _headers_rebuild(res: requests.Response) -> dict: Rebuild response headers.
        _remove_headers_duplicate(headers: dict) -> dict: Remove duplicate response headers.
        _content_type_get(headers: dict) -> str | None: Get the primary Content-Type from headers.
        _style(res: requests.Response) -> Union[bytes, str]: Style the response content based on Content-Type.

    """

    def __init__(self, url: str, internal_call: bool = False) -> None:
        self.url: str = f"https://{url}"
        self.internal_call: bool = internal_call
        self.allowed_hosts: list = ['telegram.org', 'cdn4.telegram-cdn.org']

    @staticmethod
    def _headers_rebuild(res: requests.Response) -> dict[str | Any, Any]:
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        return {
            k: MiscRegex.process_location_header(v) if k.lower() == "location" else v
            for k, v in res.raw.headers.items()
            if k.lower() not in excluded_headers
        }

    @staticmethod
    def _remove_headers_dublicate(headers: dict[str, str]) -> dict[str, str]:
        for header in ["Date", "Via", "Server"]:
            if header in headers:
                del headers[header]

        return headers

    @staticmethod
    def _content_type_get(headers: dict[str, Any]) -> str | None:
        return headers.get('Content-Type').split(';')[0]

    @staticmethod
    def _style(res: requests.Response) -> typing.Union[bytes, str]:
        """
        Style the response content based on Content-Type.

        Args:
            res (requests.Response): The HTTP response.

        Returns:
            Union[bytes, str]: The styled content.
        """

        if "Content-Type" not in res.headers.keys():
            return res.content

        content_type: str = res.headers.get("Content-Type").split(";")[0]
        position: int | None = request.args.get("before", type=int) or request.args.get("after", type=int)

        if content_type in ("text/html", "text/css", "application/json") or position:
            body = res.text

            if content_type == "application/json" and not position:
                body = MiscRegex.process_json(body)

            elif content_type == "text/html":
                # Apply custom CSS and manipulate the HTML content
                body = str(Bs4Updater(body))
                classes_to_remove = [
                    'tgme_widget_message_bubble_tail',
                    'tgme_widget_message_user',
                    'tgme_header_right_column'
                ]
                body = Bs4Updater(body).remove_by_cls(classes_to_remove)

            elif position:
                # Manipulate JSON response
                body = json.loads(body)
                classes_to_remove = [
                    'tgme_widget_message_bubble_tail',
                    'tgme_widget_message_user'
                ]
                body = Bs4Updater(body).remove_by_cls(classes_to_remove)
                body = json.dumps(body)

            return body

        return res.content

    def _request_validate(self) -> Response | typing.NoReturn:
        if not validators.url(self.url, may_have_port=False):
            return abort(400, f"Invalid URL. URL: {self.url}")

        host = urlparse(self.url).netloc.split(":")[0]
        if (host not in self.allowed_hosts) and not self.internal_call:
            return abort(403, f"Host {host} is not allowed")

    def make_request(self) -> Response | typing.NoReturn:
        """
        proxy a URL request with optional internal call.

        args:
            url (str): The URL to proxy.
            internal_call (bool, optional): Whether it's an internal call.
            defaults to False.

        returns:
            Response | typing.NoReturn: The proxied response or an error response.
        """
        self._request_validate()

        try:
            res = requests.request(
                url=self.url,
                params=request.args,
                method=request.method,
                allow_redirects=False,
                data=request.get_data(),
                cookies=request.cookies,
                headers={
                    k: v
                    for k, v in request.headers
                    if k.lower() != 'host'
                }
            )

            headers = self._headers_rebuild(res)
            headers = self._remove_headers_dublicate(headers)

            body = self._style(res)
            content_type = self._content_type_get(headers)

            position = request.args.get("before") or request.args.get("after")

            if (isinstance(body, str) and (content_type == "text/html")) or position:
                body = MiscRegex.replace_origin_host(body)

            response = Response(body, res.status_code, headers)
            return response

        except requests.exceptions.RequestException as e:
            return abort(503, str(e) if app.debug else 'hidden')

        except Exception as e:
            sentry_sdk.capture_exception(e)
            return abort(500, str(e) if app.debug else 'hidden')
