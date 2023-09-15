import json
import re

from bs4 import BeautifulSoup
from flask import request

from app import app


def schema_remove(url: str) -> str:
    """
    Remove the 'http://' or 'https://' schema from a URL.

    Args:
        url (str): The URL from which to remove the schema.

    Returns:
        str: The URL with the schema removed.
    """
    return re.sub(r"https?://", "", url)


def __url_pack(url: str) -> str:
    """
    Pack a URL with the host URL

    Args:
        url (str): The URL to pack.

    Returns:
        str: The packed URL.
    """
    return f"{request.host_url}{schema_remove(url)}"


def process_json(data: dict | list | str, url_pack=__url_pack) -> dict | list | str:
    """
    Process JSON data by recursively modifying URLs within it.

    Args:
        data (dict | list | str): The JSON data to process.
        url_pack (function): A function to pack URLs with the host URL

    Returns:
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
                new_data[key] = process_json(value, url_pack)
        return json.dumps(new_data)

    elif isinstance(data, list):
        return json.dumps([process_json(item, url_pack) for item in data])

    return data


def font_link_update(match: re.Match) -> str:
    """
    Update font links in HTML content.

    Args:
        match (re.Match): A regex match object containing the link to be updated.

    Returns:
        str: The updated URL.
    """
    original_url = "https://telegram.org" + match.group(2)
    new_url = f'{request.host_url}{schema_remove(original_url)}'
    return new_url


def process_location_header(location_header: str) -> str:
    """
    Process the 'Location' header in HTTP responses.

    Args:
        location_header (str): The 'Location' header value.

    Returns:
        str: The processed 'Location' header value with the proxy URL if needed.
    """
    proxy_url = request.host_url
    if not re.match(r'^' + re.escape(proxy_url) + r'/http://', location_header):
        original_url = re.sub(r'^http://', '', location_header)
        location_header = f'{proxy_url}{schema_remove(original_url)}'
    return location_header


def replace_origin_host(html_content: str) -> str:
    """
    Replace URLs in HTML content with proxy URLs.

    Args:
        html_content (str): The HTML content to be processed.

    Returns:
        str: The HTML content with replaced URLs.
    """
    proxy_url = request.host_url

    if should_parse_json(html_content):
        html_content = json.loads(html_content)

    soup = BeautifulSoup(html_content, 'lxml')

    replace_url_attributes(soup, proxy_url)
    replace_style_urls(soup, proxy_url)
    output = str(soup)
    output = output.replace(f'/s/{app.config["CHANNEL_NAME"]}', '')

    if should_return_json():
        output = clean_html_for_json(output)
        return json.dumps(output)

    return output


def should_parse_json(html_content: str) -> bool:
    """
    Check if JSON parsing is required based on request arguments.

    Args:
        html_content (str): The HTML content to be checked.

    Returns:
        bool: True if JSON parsing is required, False otherwise.
    """
    return any(k in ("before", "after") for k in request.args.keys())


def replace_url_attributes(soup: BeautifulSoup, proxy_url: str) -> None:
    """
    Replace URLs in specified HTML tag attributes with proxy URLs.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
        proxy_url (str): The proxy URL to prepend to the original URLs.
    """
    def update_link(tag_element: BeautifulSoup, attribute: str) -> None:
        original_url = tag_element.get(attribute)
        if original_url.split("/")[0] == "static":
            return
        if original_url:
            if original_url.startswith('//'):
                original_url = original_url.replace("//", "")
            tag_element[attribute] = f'{proxy_url}{schema_remove(original_url)}'

    for tag in soup.find_all(('script', 'img', 'video'), src=True):
        update_link(tag, 'src')

    for tag in soup.find_all('link', href=True):
        update_link(tag, 'href')


def replace_style_urls(soup: BeautifulSoup, proxy_url: str) -> None:
    """
    Replace URLs in style attributes of HTML tags with proxy URLs.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML content.
        proxy_url (str): The proxy URL to prepend to the original URLs.
    """
    def replace_url(match: re.Match) -> str:
        original_url = match.group(1)
        new_url = f'url("{proxy_url}{schema_remove(original_url)}")'
        return new_url

    for tag in soup.find_all(style=True):
        style = tag['style']
        updated_style = re.sub(r'url\([\'"]?([^\'")]+)[\'"]?\)', replace_url, style)
        tag['style'] = updated_style


def should_return_json() -> bool:
    """
    Check if JSON response should be returned based on request arguments.

    Returns:
        bool: True if JSON response should be returned, False otherwise.
    """
    return any(k in ("before", "after") for k in request.args.keys())


def clean_html_for_json(html: str) -> str:
    """
    Remove HTML and body tags for JSON response.

    Args:
        html (str): The HTML content to be cleaned.

    Returns:
        str: The cleaned HTML content.
    """
    return re.sub(r"</?html>|</?body>", "", html)
