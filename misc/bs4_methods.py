from bs4 import BeautifulSoup
from flask import url_for
import os


def _updater(
        body: str, exclude: list, selectors: dict,
        tag_s: str = "script", data: str = "src", location: str = "js"
) -> str:
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


def static_js(body: str) -> str:
    return _updater(
        body=body,
        exclude=["tgwallpaper", "jquery"],
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


def update_meta_tags(body: str) -> str:
    """
    Update the 'content' attribute of <meta> tags in an HTML document by replacing line breaks with spaces.

    Args:
        body (str): The HTML content as a string.

    Returns:
        str: The updated HTML content as a string.
    """
    # Create a BeautifulSoup object
    soup = BeautifulSoup(body, 'lxml')

    # Find all <meta> tags
    meta_tags = soup.find_all('meta')

    # Iterate through all <meta> tags
    for meta_tag in meta_tags:
        # Check if the meta-tag has a 'content' attribute
        if 'content' in meta_tag.attrs:
            # Replace line breaks with spaces in the content
            meta_tag['content'] = meta_tag['content'].replace('\n', ' ')

    # Return the updated HTML as a string
    return str(soup)


def remove_by_cls(body: str, cls_: list) -> str:
    """
    Removes elements with specified classes from the HTML document.

    Args:
        body (str): The input HTML document as a string.
        cls_ (list): A list of class names to be removed.

    Returns:
        str: The modified HTML document with specified elements removed.
    """
    # Parse the HTML document
    soup = BeautifulSoup(body, 'lxml')

    # Loop through the list of class names to remove
    for cls_i in cls_:
        # Find all elements with the specified class
        elements_to_remove = soup.find_all(class_=cls_i)

        # Remove each found element
        for element in elements_to_remove:
            element.extract()

    # Convert the modified HTML back to a string and return it
    return str(soup)


def bs_prepare(body: str) -> str:
    body = update_meta_tags(body)
    body = static_js(body)
    body = static_css(body)

    return body
