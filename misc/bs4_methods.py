from bs4 import BeautifulSoup


def add_custom_css(body: str) -> str:
    """
    Adds a custom CSS stylesheet link to the HTML document's head.

    Args:
        body (str): The input HTML document as a string.

    Returns:
        str: The modified HTML document with the added CSS link.
    """
    # Parse the HTML document
    soup = BeautifulSoup(body, 'lxml')

    # Create a new 'link' tag for the custom CSS stylesheet
    link_tag = soup.new_tag('link', href='static/css/style.css', rel='stylesheet')

    # Find the 'head' element in the HTML document and append the 'link' tag
    head = soup.find('head')
    head.append(link_tag)

    # Convert the modified HTML back to a string and return it
    return str(soup)


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


def set_bg_canvas_colors(body: str) -> str:
    """
    Sets background canvas colors by updating the 'data-colors' attribute.

    Args:
        body (str): The input HTML document as a string.

    Returns:
        str: The modified HTML document with updated 'data-colors' attribute.
    """
    # Parse the HTML document
    soup = BeautifulSoup(body, 'lxml')

    # Find the canvas element with the specified id
    canvas = soup.find(id='tgme_background')

    # Define the new colors
    new_colors = "fdb219,3c3c86,fdb219,3c3c86"

    # Update the 'data-colors' attribute with the new colors
    canvas['data-colors'] = new_colors

    # Convert the modified HTML back to a string and return it
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
