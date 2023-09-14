import importlib
import logging
import os

views = [
    f for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
    if f.endswith(".py") and f != "__init__.py"
]


for view in views:
    importlib.import_module(
        os.path.dirname(
            os.path.realpath(__file__)
        ).split('/')[-1] + "." + view[:-3]
    )
    logging.info(f'App imported {view} successfully.')
