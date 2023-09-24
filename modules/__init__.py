import importlib
import os

from app import app

# Get a list of Python files (views) in the current directory
views = [
    f for f in os.listdir(os.path.dirname(os.path.abspath(__file__)))
    if f.endswith(".py") and f != "__init__.py"
]

# Iterate through each view and import it dynamically
for view in views:
    # Construct the module name based on the file name
    module_name = os.path.dirname(os.path.realpath(__file__)).split('/')[-1] + "." + view[:-3]

    try:
        # Import the module dynamically
        importlib.import_module(module_name)
        app.logger.debug(f'App imported {view} successfully.')
    except ImportError as e:
        app.logger.error(f'Error importing {view}: {str(e)}')
