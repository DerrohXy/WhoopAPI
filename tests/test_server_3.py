import json
import os.path

from src.whoopapi import (
    LOG_ERROR,
    LOG_PRETTY,
    Application,
    HttpRequest,
    HttpResponse,
    WebsocketHandler,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_DIR = os.path.join(BASE_DIR, "private")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SSL_CERT_FILE = os.path.join(PRIVATE_DIR, "sslcertificate.crt")
SSL_KEY_FILE = os.path.join(PRIVATE_DIR, "sslkey.key")


middlewares = [
    lambda x: x.set_context_key("key1", "value1"),
    lambda x: x.set_context_key("key2", "value2"),
]
application = Application()
# application.set_ssl(SSL_CERT_FILE,SSL_KEY_FILE)

for action in middlewares:
    application.add_middleware(action)


@application.route(path="/", methods=["GET"])
def IndexHandler(request: HttpRequest):
    response = HttpResponse()
    response.set_json(
        {
            "message": "This is the index page",
            "path": request.path,
            "params": request.query_params,
            "protocol": request.protocol,
            "method": request.method,
            "host": request.host,
        }
    )

    return response


@application.route(path="/random", methods=["GET"])
def RandomHandler(request: HttpRequest):
    response = {
        "message": "This is the index page",
        "path": request.path,
        "params": request.query_params,
        "protocol": request.protocol,
        "method": request.method,
        "host": request.host,
    }

    return response


@application.route(path="/form")
def PostFormHandler(request: HttpRequest):
    response = HttpResponse()

    result = {
        "data": request.body.form_data,
        "files": [k for k, v in (request.body.files or {}).items()],
    }

    response.set_json(result)

    return response


@application.route(path="/json")
def PostJsonHandler(request: HttpRequest):
    response = request.body.json

    return response


@application.route_ws(path="/ws1")
class WsHandler(WebsocketHandler):
    def on_message(self, message: bytes):
        response = json.dumps(
            {
                "received": str(message),
                "responding": f"Random response to {str(message)}",
            }
        )
        self.send(response)

    def on_error(self, exception):
        LOG_PRETTY(exception)

    def on_connect(self, request: HttpRequest):
        LOG_ERROR("Websocket connected")

    def on_close(self):
        LOG_ERROR("Websocket closed.")


application.listen(
    on_start=lambda x: LOG_ERROR(f"Testing server running on port {x[1]}")
)
