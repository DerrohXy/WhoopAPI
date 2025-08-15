import socket as SOCKET
import ssl as SSL
import sys
import threading as THREADING
from typing import Callable
from urllib.parse import urlparse

import src.constants as CONSTANTS
from src.constants import HttpMethods
from src.logging import LOG_ERROR, LOG_PRETTY
from src.parsers.http_body import parse_body
from src.parsers.http_headers import parse_headers
from src.protocol_handlers.http import RequestHandler, handle_http_client_request
from src.protocol_handlers.websocket import (
    WebsocketHandler,
    handle_websocket_client_request,
    perform_websocket_handshake,
)
from src.wrappers import HttpRequest


def read_http_client_request_body(socket: SOCKET.socket, body_size: int):
    LOW_THRESHOLD = 1024
    buffer = b""
    if body_size == 0:
        return buffer

    if body_size < 0:
        body_size = sys.maxsize

    if body_size <= LOW_THRESHOLD:
        return socket.recv(body_size)

    else:
        buffer = b""
        bytes_read = 0
        bytes_remaining = body_size

        while True:
            if bytes_remaining < LOW_THRESHOLD:
                buffer = buffer + socket.recv(bytes_remaining)

                break

            else:
                chunk = socket.recv(LOW_THRESHOLD)
                if len(chunk) < LOW_THRESHOLD:
                    bytes_remaining = 0

                buffer = buffer + chunk
                bytes_read = bytes_read + LOW_THRESHOLD
                bytes_remaining = body_size - bytes_read

        return buffer


def read_http_client_request_headers(socket: SOCKET.socket):
    HEADERS_BREAK = b"\r\n\r\n"
    buffer = b""
    while True:
        data = socket.recv(1)
        if data:
            buffer = buffer + data
            if buffer.endswith(HEADERS_BREAK):
                break

    return buffer[: -len(HEADERS_BREAK)]


def read_http_client_request(socket: SOCKET.socket):
    try:
        headers_data = read_http_client_request_headers(socket=socket)
        parsed_headers = parse_headers(headers_data)

        headers = parsed_headers["headers"]
        header_params = parsed_headers["header_params"]
        request_info = parsed_headers["request_info"]

        if request_info.get("method", "get").lower() == HttpMethods.GET:
            body_size = 0

        else:
            body_size = int(headers.get(CONSTANTS.HttpHeaders.CONTENT_LENGTH, -1))

        body_data = read_http_client_request_body(socket, body_size)
        parsed_body = parse_body(headers, header_params, body_data)

        http_request = HttpRequest(
            request_info=request_info,
            request_header_params=header_params,
            request_headers=headers,
            request_body=parsed_body,
        )

        return http_request, None

    except Exception as e:
        return None, f"{e}"


def parse_route_path(path: str):
    parsed = urlparse(url=path)
    return parsed.path


class WebServer:
    def __init__(self):
        self.middlewares = []
        self.http_routes = []
        self.websocket_routes = []
        self.ssl_cert_file = None
        self.ssl_key_file = None

    def set_ssl(self, cert_file: str, key_file: str):
        self.ssl_cert_file = cert_file
        self.ssl_key_file = key_file

    def add_middleware(self, *middlewares: Callable):
        self.middlewares = [*self.middlewares, *middlewares]

    def route_http(self, path: str, handler: Callable | RequestHandler):
        self.http_routes = [*self.http_routes, (parse_route_path(path=path), handler)]

    def route_websocket(self, path: str, handler: Callable | WebsocketHandler):
        self.websocket_routes = [
            *self.websocket_routes,
            (parse_route_path(path=path), handler),
        ]

    def clear_middlewares(self):
        self.middlewares = []

    def clear_http_routes(self):
        self.http_routes = []

    def clear_websocket_routes(self):
        self.websocket_routes = []

    def execute_request(self, request: HttpRequest):
        handle_http_client_request(
            request=request, middlewares=self.middlewares, http_routes=self.http_routes
        )

    def listen(self, port: int | str = 8000, on_start: Callable = None):
        bind_address = ("", int(port))

        start_web_server(
            bind_address=bind_address,
            server=self,
            on_start=on_start,
            ssl_cert_file=self.ssl_cert_file,
            ssl_key_file=self.ssl_key_file,
        )


def handle_client_connection(
    socket: SOCKET.socket,
    server: WebServer,
):
    http_request, error = read_http_client_request(socket)
    if error:
        LOG_ERROR(error)
        socket.close()

    else:
        request_protocol = http_request.protocol.lower()

        if request_protocol.lower() in [
            CONSTANTS.WebProtocols.HTTP,
            CONSTANTS.WebProtocols.HTTPS,
        ]:
            request_headers = http_request.headers

            connection = request_headers.get(CONSTANTS.HttpHeaders.CONNECTION, "")
            upgrade = request_headers.get(CONSTANTS.HttpHeaders.UPGRADE, "")

            handler_response = None
            if connection and connection.lower() == "upgrade":
                if upgrade and upgrade.lower() == "websocket":
                    handshake_successful = perform_websocket_handshake(
                        socket, request_headers
                    )
                    if handshake_successful:
                        handle_websocket_client_request(
                            socket=socket,
                            request=http_request,
                            middlewares=server.middlewares,
                            websocket_routes=server.websocket_routes,
                        )

                    else:
                        handler_response = handle_http_client_request(
                            request=http_request,
                            middlewares=server.middlewares,
                            http_routes=server.http_routes,
                        )

            else:
                handler_response = handle_http_client_request(
                    request=http_request,
                    middlewares=server.middlewares,
                    http_routes=server.http_routes,
                )

            result = handler_response.build(request_headers=request_headers)
            socket.sendall(result)
            socket.close()

        else:
            socket.close()


def start_web_server(
    bind_address: tuple[str, int],
    server: WebServer,
    on_start: Callable,
    ssl_cert_file: str = None,
    ssl_key_file: str = None,
):
    server.http_routes.sort(key=lambda x: len(x[0]), reverse=True)
    server.websocket_routes.sort(key=lambda x: len(x[0]), reverse=True)

    server_socket = SOCKET.socket(SOCKET.AF_INET, SOCKET.SOCK_STREAM)
    server_socket.bind(bind_address)
    server_socket.listen(1000)

    if callable(on_start):
        on_start(bind_address)

    else:
        LOG_ERROR(f"Server running on port {bind_address[1]}")

    while True:
        client_socket, client_address = server_socket.accept()
        if ssl_cert_file and ssl_key_file:
            ssl_context = SSL.SSLContext(SSL.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile=ssl_cert_file, keyfile=ssl_key_file)

            try:
                client_socket = ssl_context.wrap_socket(client_socket, server_side=True)

            except Exception as e:
                LOG_PRETTY(e)

        try:
            client_thread = THREADING.Thread(
                target=handle_client_connection,
                args=(client_socket, server),
            )
            client_thread.start()

        except Exception as e:
            LOG_PRETTY(e)
