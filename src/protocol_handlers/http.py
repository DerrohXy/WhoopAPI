import os
from typing import Any, Callable, Optional

import src.constants as CONSTANTS
from src import LOG_ERROR
from src.logging import LOG_INFO
from src.responses import DEFAULT_404_PAGE
from src.wrappers import HttpRequest, HttpResponse


class RequestHandler:
    def __init__(self):
        self.route = ""

    def get(self, request: HttpRequest) -> Optional[Any]:
        pass

    def post(self, request: HttpRequest) -> Optional[Any]:
        pass

    def put(self, request: HttpRequest) -> Optional[Any]:
        pass

    def delete(self, request: HttpRequest) -> Optional[Any]:
        pass


def path_matches_route(path: str, route: str):
    return path.strip("/ ") == route.strip("/ ")


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
    response_code = CONSTANTS.HttpStatusCodes.C_200

    handler_found = False
    for route, handler_function in http_routes:
        if isinstance(handler_function, RequestHandler):
            handler = handler_function

        else:
            handler = handler_function()

        if path_matches_route(path=request_path, route=route):
            handler.route = route
            try:
                if request_method == CONSTANTS.HttpMethods.GET:
                    response = handler.get(request)
                    handler_found = True

                elif request_method == CONSTANTS.HttpMethods.POST:
                    response = handler.post(request)
                    handler_found = True

                elif request_method == CONSTANTS.HttpMethods.PUT:
                    response = handler.put(request)
                    handler_found = True

                elif request_method == CONSTANTS.HttpMethods.DELETE:
                    response = handler.delete(request)
                    handler_found = True

            except Exception as e:
                LOG_ERROR(e)
                response = HttpResponse()
                response.set_status_code(CONSTANTS.HttpStatusCodes.C_500)
                response.set_html(DEFAULT_404_PAGE)
                response_code = response.status_code

            break

    if isinstance(response, HttpResponse):
        response_code = response.status_code
        wrapped_response = response

    elif isinstance(response, str):
        text_response = HttpResponse()
        text_response.set_header(
            CONSTANTS.HttpHeaders.CONTENT_TYPE, CONSTANTS.HttpContentTypes.TEXT_PLAIN
        )
        text_response.set_body(response)
        wrapped_response = text_response

    elif isinstance(response, dict) or isinstance(response, list):
        json_response = HttpResponse()
        json_response.set_json(response)
        wrapped_response = json_response

    elif (not handler_found) or (not response):
        response = HttpResponse()
        response.set_status_code(CONSTANTS.HttpStatusCodes.C_404)
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
