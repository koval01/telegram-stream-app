from bs4 import BeautifulSoup
from flask import url_for
import os


class Bs4Updater:
    """
    A utility class for updating attributes of HTML tags in an HTML document using BeautifulSoup.

    This class provides methods to update attributes like 'src' and 'href' of <script> and <link> tags,
    as well as modify the 'content' attribute of <meta> tags. It can also remove elements with specific
    class names from the HTML document.

    Args:
        body (str): The HTML document as a string.

    Attributes:
        soup (BeautifulSoup): A BeautifulSoup object representing the parsed HTML document.
    """

    def __init__(self, body: str) -> None:
        self.soup = BeautifulSoup(body, 'lxml')

    def _updater(
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
            new_src = url_for('static', filename=f'{location}/{file_name}')[1:]
            tag[data] = new_src

    def _update_meta_tags(self) -> None:
        """
        Update the 'content' attribute of <meta> tags in an HTML document by replacing line breaks with spaces.
        """

        for tag in self.soup.find_all('meta'):
            if 'content' in tag.attrs:
                # Replace newline characters with spaces in the 'content' attribute
                tag['content'] = tag['content'].replace('\n', ' ')

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
        self._updater(
            exclude=["tgwallpaper"],
            selectors={"src": True},
            tag_s="script",
            data="src",
            location="js"
        )

    def _static_css(self) -> None:
        self._updater(
            exclude=[],
            selectors={"href": True, "rel": "stylesheet"},
            tag_s="link",
            data="href",
            location="css"
        )

    def __str__(self) -> str:
        self._update_meta_tags()
        self._static_js()
        self._static_css()

        return str(self.soup)
