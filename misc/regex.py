import re

from bs4 import BeautifulSoup
from flask import Request

from misc.crypt import Crypt


def __get_file_extension(url):
    # Split the URL by the dot (.) to get the parts of the URL
    parts = url.split('.')
    # The last part should be the file extension
    if len(parts) > 1:
        extension = '.' + parts[-1]
        return extension.split("?")[0]
    else:
        return ""


def process_location_header(location_header: str, request: Request):
    proxy_url = request.host_url

    # Check if the location_header already contains the proxy URL
    if not re.match(r'^' + re.escape(proxy_url) + r'/http://', location_header):
        # Extract the original URL from the location_header
        original_url = re.sub(r'^http://', '', location_header)

        # Append the proxy URL to the original URL
        location_header = f'{proxy_url}/{original_url}'

    return location_header


def replace_origin_host(html_content: str, request: Request) -> str:
    proxy_url = request.host_url

    soup = BeautifulSoup(html_content, 'lxml')

    # Define a function to update a single link
    def update_link(tag, attribute):
        original_url = tag.get(attribute)
        if original_url:
            # Check if the URL starts with "//" and add "http:" if needed
            if original_url.startswith('//'):
                original_url = 'https:' + original_url

            # Replace the original URL with the proxy URL
            tag[attribute] = f'{proxy_url}{Crypt().enc(original_url) + __get_file_extension(original_url)}'

    # Update links in different HTML elements
    for tag in soup.find_all(['script', 'link', 'img', 'video'], src=True):
        update_link(tag, 'src')

    def replace_url(match):
        # Extract the URL from the match
        original_url = match.group(1)

        # Edit the original URL if needed
        # For example, you can add query parameters or modify it in any other way
        edited_url = Crypt().enc(original_url) + __get_file_extension(original_url)

        # Construct the new URL with the proxy URL
        new_url = f'url("{proxy_url}{edited_url}")'

        return new_url

    # Update background-image in style attributes
    for tag in soup.find_all(style=True):
        style = tag['style']
        updated_style = re.sub(r'url\([\'"]?([^\'")]+)[\'"]?\)', replace_url, style)
        tag['style'] = updated_style

    # Return the updated HTML content
    return str(soup)
