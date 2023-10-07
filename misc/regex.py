import json
import re

from bs4 import BeautifulSoup
from flask import request, g

from app import app


class MiscRegex:
    """
    A utility class for handling various operations related to JSON data processing and URL manipulation in HTML content
    """
    proxy_path: str = app.config["PROXY_PATH"]

    @staticmethod
    def _schema_remove(url: str) -> str:
        return re.sub(r"https?://", "", url)

    @staticmethod
    def _should_json() -> bool:
        return any(k in ("before", "after") for k in request.args.keys())

    @staticmethod
    def _clean_html_for_json(html: str) -> str:
        return re.sub(r"</?html>|</?body>", "", html)

    @staticmethod
    def _url_pack(url: str) -> str:
        return f"{request.host_url}{MiscRegex.proxy_path}/{MiscRegex._schema_remove(url)}"

    @classmethod
    def process_json(cls, data: dict | list | str, url_pack=_url_pack) -> dict | list | str:
        """
        process JSON data by recursively modifying URLs within it.

        args:
            data (dict | list | str): The JSON data to process.
            url_pack (function): A function to pack URLs with the host URL

        returns:
            dict | list | str: The processed JSON data.
        """

        if isinstance(data, str):
            if len(data) < 10:
                return data
            try:
                data = json.loads(data)
            except ValueError:
                return data

        if isinstance(data, dict):
            new_data = {}
            for key, value in data.items():
                if isinstance(value, str) and value.startswith("http"):
                    new_data[key] = url_pack(value)
                else:
                    new_data[key] = cls.process_json(value, url_pack)
            return json.dumps(new_data)

        elif isinstance(data, list):
            return json.dumps([cls.process_json(item, url_pack) for item in data])

        return data

    @classmethod
    def process_location_header(cls, location_header: str) -> str:
        """
        Process the 'Location' header in HTTP responses.

        Args:
            location_header (str): The 'Location' header value.

        Returns:
            str: The processed 'Location' header value with the proxy URL if needed.
        """

        proxy_url = f"{request.host_url}{cls.proxy_path}/"

        if not re.match(
                r'^' + re.escape(proxy_url) + r'http://',
                location_header
        ):
            original_url = re.sub(r'^http://', '', location_header)
            location_header = f'{proxy_url}{cls._schema_remove(original_url)}'

        return location_header

    @staticmethod
    def _is_static(url: str) -> bool:
        return url.startswith(f"{app.static_url_path}/")

    @classmethod
    def replace_origin_host(cls, html_content: str) -> str:
        """
        Replace URLs in HTML content with proxy URLs.

        Args:
            html_content (str): The HTML content to be processed.

        Returns:
            str: The HTML content with replaced URLs.
        """

        proxy_url = f"{request.host_url}{cls.proxy_path}/"

        if cls._should_json():
            html_content = json.loads(html_content)

        soup = BeautifulSoup(html_content, 'lxml')

        cls.replace_url_attributes(soup, proxy_url)
        cls.replace_style_urls(soup, proxy_url)

        output = str(soup)
        output = output.replace(f'/s/{g.channel_name}'[:-1], '')

        if cls._should_json():
            output = cls._clean_html_for_json(output)
            return json.dumps(output)

        return output

    @classmethod
    def replace_url_attributes(cls, soup: BeautifulSoup, proxy_url: str) -> None:
        """
        replace URLs in specified HTML tag attributes with proxy URLs.

        args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
            proxy_url (str): The proxy URL to prepend to the original URLs.
        """

        def _update_link(tag_element: BeautifulSoup, attribute: str) -> None:
            original_url = tag_element.get(attribute)
            if cls._is_static(original_url):
                return
            if any([original_url.startswith(v) for v in ["data:", "svg+"]]):
                return
            if original_url:
                if original_url.startswith('//'):
                    original_url = original_url.replace("//", "")
                tag_element[attribute] = f'{proxy_url}{cls._schema_remove(original_url)}'

        for tag in soup.find_all(('script', 'img', 'video'), src=True):
            _update_link(tag, 'src')

        for tag in soup.find_all('link', href=True):
            _update_link(tag, 'href')

        for tag in soup.find_all('source', srcset=True):
            _update_link(tag, 'srcset')

    @classmethod
    def replace_style_urls(cls, soup: BeautifulSoup, proxy_url: str) -> None:
        """
        replace URLs in style attributes of HTML tags with proxy URLs.

        args:
            soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
            proxy_url (str): The proxy URL to prepend to the original URLs.
        """

        def replace_url(match: re.Match) -> str:
            original_url = match.group(1)
            new_url = f'url("{proxy_url}{cls._schema_remove(original_url).replace("//", "")}")'
            return new_url

        for tag in soup.find_all(style=True):
            style = tag['style']
            updated_style = re.sub(r'url\([\'"]?([^\'")]+)[\'"]?\)', replace_url, style)
            tag['style'] = updated_style
