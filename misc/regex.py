import json
import re

from bs4 import BeautifulSoup
from flask import request

from app import app
from misc.crypt import Crypt


def get_file_extension(url: str) -> str:
    """
    Extracts the file extension from a URL.

    Args:
        url (str): The URL from which to extract the file extension.

    Returns:
        str: The extracted file extension (including the dot).
    """
    parts = url.split('.')
    if len(parts) > 1:
        extension = '.' + parts[-1]
        return extension.split("?")[0]
    else:
        return ""


def font_link_update(match: re.Match) -> str:
    """
    Update font links in HTML content.

    Args:
        match (re.Match): A regex match object containing the link to be updated.

    Returns:
        str: The updated URL.
    """
    original_url = "https://telegram.org" + match.group(2)
    edited_url = Crypt().enc(original_url) + get_file_extension(original_url)
    new_url = f'{request.host_url}{edited_url}'
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
        location_header = f'{proxy_url}/{original_url}'
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
    if "before" in request.args.keys():
        html_content = json.loads(html_content)
    soup = BeautifulSoup(html_content, 'lxml')

    def update_link(tag_element: BeautifulSoup, attribute: str) -> None:
        original_url = tag_element.get(attribute)
        if original_url.split("/")[0] == "static":
            return
        if original_url:
            if original_url.startswith('//'):
                original_url = 'https:' + original_url
            tag_element[attribute] = f'{proxy_url}{Crypt().enc(original_url) + get_file_extension(original_url)}'

    for tag in soup.find_all(['script', 'img', 'video'], src=True):
        update_link(tag, 'src')

    for tag in soup.find_all(['link'], href=True):
        update_link(tag, 'href')

    def replace_url(match: re.Match) -> str:
        original_url = match.group(1)
        edited_url = Crypt().enc(original_url) + get_file_extension(original_url)
        new_url = f'url("{proxy_url}{edited_url}")'
        return new_url

    for tag in soup.find_all(style=True):
        style = tag['style']
        updated_style = re.sub(r'url\([\'"]?([^\'")]+)[\'"]?\)', replace_url, style)
        tag['style'] = updated_style

    output = str(soup)
    output = output.replace(f'/s/{app.config["CHANNEL_NAME"]}', '/')

    if "before" in request.args.keys():
        output = re.sub(r"</?html>|</?body>", "", output)
        return json.dumps(output)

    return output
