import os

from flask import Flask
from websocket import websocket_app

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.debug = True

def my_app(environ, start_response):
    path = environ["PATH_INFO"]
    if path == "/":
        return app(environ, start_response)
    elif path == "/websocket":
        websocket_app(environ["wsgi.websocket"])
    else:
        return app(environ, start_response)

import views