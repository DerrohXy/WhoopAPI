import json
import os.path

from src import (
    CONSTANTS,
    LOG_ERROR,
    LOG_PRETTY,
    HttpRequest,
    HttpResponse,
    RequestHandler,
    StaticFileHandler,
    WebServer,
    WebsocketHandler,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRIVATE_DIR = os.path.join(BASE_DIR, "private")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
STATIC_DIR = os.path.join(BASE_DIR, "static")
SSL_CERT_FILE = os.path.join(PRIVATE_DIR, "sslcertificate.crt")
SSL_KEY_FILE = os.path.join(PRIVATE_DIR, "sslkey.key")


class IndexHandler(RequestHandler):
    def get(self, request: HttpRequest):
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


class RandomHandler(RequestHandler):
    def get(self, request: HttpRequest):
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


class PostFormHandler(RequestHandler):
    def post(self, request: HttpRequest):
        response = HttpResponse()

        result = {
            "data": request.body.form_data,
            "files": [k for k, v in (request.body.files or {}).items()],
        }
        print(result)

        response.set_json(result)

        return response


class PostJsonHandler(RequestHandler):
    def post(self, request: HttpRequest):
        response = HttpResponse()

        result = request.body.json
        print(result)

        response.set_json(result)

        return response


class WsHandler(WebsocketHandler):
    def on_message(self, message: bytes):
        # LOG("Message received")
        # LOG_PRETTY(message)
        response = json.dumps(
            {"received": str(message), "responding": "Random response"}
        )
        self.send(response)

    def on_error(self, exception):
        LOG_PRETTY(exception)

    def on_connect(self, request: HttpRequest):
        LOG_ERROR("Websocket connected")

    def on_close(self):
        LOG_ERROR("Websocket closed.")


if __name__ == "__main__":
    http_routes = [
        ("/", IndexHandler),
        ("/random", RandomHandler),
        ("/form", PostFormHandler),
        ("/json", PostJsonHandler),
        ("/static", StaticFileHandler(directories=[STATIC_DIR])),
    ]
    websocket_routes = [
        ("/ws1", WsHandler),
        ("/ws2", WsHandler),
    ]
    middlewares = [
        lambda x: x.set_context_key("key1", "value1"),
        lambda x: x.set_context_key("key2", "value2"),
    ]
    web_server = WebServer()
    # web_server.set_ssl(SSL_CERT_FILE,SSL_KEY_FILE)

    for action in middlewares:
        web_server.add_middleware(action)

    for path, handler in http_routes:
        web_server.route_http(path, handler)

    for path, handler in websocket_routes:
        web_server.route_websocket(path, handler)

    web_server.listen(
        on_start=lambda x: LOG_ERROR(f"Testing server running on port {x[1]}")
    )
