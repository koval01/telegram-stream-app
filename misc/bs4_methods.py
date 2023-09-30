from bs4 import BeautifulSoup
from flask import url_for
import os


def _updater(
        body: str, exclude: list, selectors: dict,
        tag_s: str = "script", data: str = "src", location: str = "js"
) -> str:
    """
    Helper function to update attributes of HTML tags with specified selectors.

    Args:
        body (str): The HTML content as a string.
        exclude (list): List of substrings to exclude from updates.
        selectors (dict): Dictionary of attributes to select tags with.
        tag_s (str): The HTML tag type to select (e.g., 'script' or 'link').
        data (str): The attribute to update (e.g., 'src' or 'href').
        location (str): The location to use for replacements (e.g., 'js' or 'css').

    Returns:
        str: The updated HTML content as a string.
    """

    soup = BeautifulSoup(body, 'lxml')

    tags = soup.find_all(tag_s, **selectors)

    for tag in tags:
        old_src = tag[data].split("?")[0]
        file_name = os.path.basename(old_src)

        if any([(e in file_name) for e in exclude]):
            tag.extract()
            continue

        # set new var
        new_src = url_for('static', filename=f'{location}/{file_name}')[1:]
        tag[data] = new_src

    return str(soup)


def update_meta_tags(body: str) -> str:
    """
    Update the 'content' attribute of <meta> tags in an HTML document by replacing line breaks with spaces.

    Args:
        body (str): The HTML content as a string.

    Returns:
        str: The updated HTML content as a string.
    """

    soup = BeautifulSoup(body, 'lxml')

    for tag in soup.find_all('meta'):
        if 'content' in tag.attrs:
            # Replace newline characters with spaces in the 'content' attribute
            tag['content'] = tag['content'].replace('\n', ' ')

    return str(soup)


def remove_by_cls(body: str, cls_list: list) -> str:
    """
    Removes elements with specified classes from the HTML document.

    Args:
        body (str): The input HTML document as a string.
        cls_list (list): A list of class names to be removed.

    Returns:
        str: The modified HTML document with specified elements removed.
    """

    soup = BeautifulSoup(body, 'lxml')

    for cls in cls_list:
        # Find and remove all elements with the specified class
        for element in soup.find_all(class_=cls):
            element.extract()

    return str(soup)


def static_js(body: str) -> str:
    return _updater(
        body=body,
        exclude=["tgwallpaper"],
        selectors={"src": True},
        tag_s="script",
        data="src",
        location="js"
    )


def static_css(body: str) -> str:
    return _updater(
        body=body,
        exclude=[],
        selectors={"href": True, "rel": "stylesheet"},
        tag_s="link",
        data="href",
        location="css"
    )


def bs_prepare(body: str) -> str:
    return static_css(static_js(update_meta_tags(body)))
