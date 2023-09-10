from bs4 import BeautifulSoup


def add_custom_css(body: str) -> str:
    soup = BeautifulSoup(body, 'lxml')

    link_tag = soup.new_tag('link', href='static/css/style.css', rel='stylesheet')

    head = soup.find('head')
    head.append(link_tag)
    return str(soup)


def set_bg_canvas_colors(body: str) -> str:
    soup = BeautifulSoup(body, 'lxml')

    canvas = soup.find(id='tgme_background')

    new_colors = "aba048,557ead,b0a971,5c8dc4"
    canvas['data-colors'] = new_colors

    return str(soup)


def remove_by_cls(body: str, cls_: list) -> str:
    soup = BeautifulSoup(body, 'lxml')

    for cls_i in cls_:
        elements_to_remove = soup.find_all(class_=cls_i)

        for element in elements_to_remove:
            element.extract()

    return str(soup)
