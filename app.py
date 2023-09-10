from flask import Flask
from flask_minify import Minify


app = Flask(__name__)
Minify(app=app, html=True, js=True, cssless=True)


import modules
