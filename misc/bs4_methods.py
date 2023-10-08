from bs4 import BeautifulSoup
from flask import url_for, g, request
from app import app
import os


class Bs4Updater:
    """
    A utility class for updating and manipulating HTML content using BeautifulSoup.

    Args:
        body (str): The HTML content to be processed.
    """

    def __init__(self, body: str) -> None:
        self.soup = BeautifulSoup(body, 'lxml')
        self.channel_name: str = g.channel_name

    def _path_updater(
            self, exclude: list, selectors: dict,
            tag_s: str = "script", data: str = "src", location: str = "js"
    ) -> None:
        """
        Helper function to update attributes of HTML tags with specified selectors.

        Args:
            exclude (list): List of substrings to exclude from updates.
            selectors (dict): Dictionary of attributes to select tags with.
            tag_s (str): The HTML tag type to select (e.g., 'script' or 'link').
            data (str): The attribute to update (e.g., 'src' or 'href').
            location (str): The location to use for replacements (e.g., 'js' or 'css').
        """

        tags = self.soup.find_all(tag_s, **selectors)

        for tag in tags:
            old_src = tag[data].split("?")[0]
            file_name = os.path.basename(old_src)

            if any([(e in file_name) for e in exclude]):
                tag.extract()
                continue

            # set new var
            tag[data] = url_for('static', filename=f'{location}/{file_name}')

    def _update_meta_tags(self) -> None:
        for tag in self.soup.find_all('meta'):
            if 'content' in tag.attrs:
                # Replace newline characters with spaces in the 'content' attribute
                tag['content'] = tag['content'].replace('\n', ' ')

    def _replace_links(self) -> None:
        for a_tag in self.soup.find_all('a', href=True):
            if a_tag['rel'] in ("canonical", "prev",):
                return

            # Replace the href attribute with a new link
            a_tag['href'] = a_tag['href'].replace(f"https://t.me/{self.channel_name}/", "/")

    def remove_by_cls(self, cls_list: list) -> str:
        """
        Removes elements with specified classes from the HTML document.

        Args:
            cls_list (list): A list of class names to be removed.

        Returns:
            str: The modified HTML document with specified elements removed.
        """

        for cls in cls_list:
            # Find and remove all elements with the specified class
            for element in self.soup.find_all(class_=cls):
                element.extract()

        return str(self.soup)

    def _static_js(self) -> None:
        self._path_updater(
            exclude=["tgwallpaper"],
            selectors={"src": True},
            tag_s="script",
            data="src",
            location="js"
        )

    def _static_css(self) -> None:
        self._path_updater(
            exclude=[],
            selectors={"href": True, "rel": "stylesheet"},
            tag_s="link",
            data="href",
            location="css"
        )

    def __str__(self) -> str:
        self._update_meta_tags()
        self._replace_links()
        self._static_js()
        self._static_css()

        return str(self.soup)
