from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

def websocket_app(environ):
    if environ["PATH_INFO"] == '/connect':
        ws = environ["wsgi.websocket"]
        message = ws.receive()
        ws.send(message)

server = pywsgi.WSGIServer(("", 5000), websocket_app,
    handler_class=WebSocketHandler)
server.serve_forever()