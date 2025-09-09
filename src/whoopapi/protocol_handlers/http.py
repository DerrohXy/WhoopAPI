import inspect
import os
from typing import Any, Callable, Optional

from ..constants import HttpContentTypes, HttpHeaders, HttpStatusCodes
from ..logging import LOG_ERROR, LOG_INFO
from ..responses import DEFAULT_404_PAGE
from ..wrappers import HttpRequest, HttpResponse


class RequestHandler:
    def __init__(self):
        self.route = ""

    def get_handler_for_method_(self, method: str) -> Callable[[HttpRequest], Any]:
        handler_ = {
            "get": self.get,
            "post": self.post,
            "put": self.put,
            "patch": self.patch,
            "delete": self.delete,
        }.get(method, None)

        if not handler_:
            raise Exception(f"Unable to get handler for method : {method}.")

        return handler_

    def get(self, request: HttpRequest) -> Optional[Any]:
        pass

    def post(self, request: HttpRequest) -> Optional[Any]:
        pass

    def put(self, request: HttpRequest) -> Optional[Any]:
        pass

    def patch(self, request: HttpRequest) -> Optional[Any]:
        pass

    def delete(self, request: HttpRequest) -> Optional[Any]:
        pass


def path_matches_route(path: str, route: str):
    route_ = route.strip("/ ")
    path_ = path.strip("/ ")
    return path_.startswith(route_)


def handle_http_client_request(
    request: HttpRequest,
    middlewares: list[Callable],
    http_routes: list[tuple[str, Callable | RequestHandler]],
    log_handler=True,
):
    for action in middlewares:
        action(request)

    response = None
    wrapped_response = None
    request_method = request.method.lower()
    request_path = request.path
    request_protocol = request.protocol
    response_code = HttpStatusCodes.C_200

    handler_found = False
    for route, handler_function in http_routes:
        if isinstance(handler_function, RequestHandler):
            handler = handler_function
            handler.route = route
            handler_function_ = handler_function.get_handler_for_method_(
                method=request_method
            )

        elif inspect.isclass(handler_function) and issubclass(
            handler_function, RequestHandler
        ):
            handler = handler_function()
            handler.route = route
            handler_function_ = handler.get_handler_for_method_(method=request_method)

        elif inspect.isfunction(handler_function):
            handler_function_ = handler_function

        else:
            raise Exception(
                "Invalid websocket handler. Must be Class_(RequestHandler), or instance of."
            )

        if path_matches_route(path=request_path, route=route):
            handler_found = True

            try:
                response = handler_function_(request)

            except Exception as e:
                LOG_ERROR(e)
                response = HttpResponse()
                response.set_status_code(HttpStatusCodes.C_500)
                response.set_html(DEFAULT_404_PAGE)
                response_code = response.status_code

            break

    if isinstance(response, HttpResponse):
        response_code = response.status_code
        wrapped_response = response

    elif isinstance(response, str):
        text_response = HttpResponse()
        text_response.set_header(HttpHeaders.CONTENT_TYPE, HttpContentTypes.TEXT_PLAIN)
        text_response.set_body(response)
        wrapped_response = text_response

    elif isinstance(response, dict) or isinstance(response, list):
        json_response = HttpResponse()
        json_response.set_json(response)
        wrapped_response = json_response

    elif (not handler_found) or (not response):
        response = HttpResponse()
        response.set_status_code(HttpStatusCodes.C_404)
        response.set_html(DEFAULT_404_PAGE)
        response_code = response.status_code
        wrapped_response = response

    if log_handler:
        log_message = f"{request_method.upper()} {request_protocol.upper()}://{request.host}{request_path} {response_code}"
        LOG_INFO(log_message)

    return wrapped_response


class StaticFileHandler(RequestHandler):
    def __init__(self, directories: list[str] = None):
        super().__init__()
        self.directories = directories or []

    def get_file_path(self, path: str):
        file_path = path[len(self.route) + 1 :]

        for directory in self.directories:
            file_path = os.path.join(directory, file_path)
            if os.path.exists(file_path):
                return file_path

        return None

    def get(self, request: HttpRequest):
        file_path = self.get_file_path(request.path)
        if file_path:
            file = open(file_path, "rb")
            data = file.read()
            file.close()
            response = HttpResponse()
            response.set_file(f"{file_path.split(os.path.sep)[-1]}", data)

            return response

        else:
            return None
