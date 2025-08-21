import gzip
import json as JSON
import zlib
from typing import Optional

import brotli

import src.constants as CONSTANTS
from src.constants import get_content_type_from_filename


class HttpRequestBody:
    def __init__(self, **kwargs):
        self.json = kwargs.get("json", None)
        self.form_data = kwargs.get("form_data", None)
        self.files = kwargs.get("files", None)
        self.raw = kwargs.get("raw", None)


class HttpRequest:
    def __init__(
        self,
        request_info: Optional[dict] = None,
        request_headers: Optional[dict] = None,
        request_header_params: Optional[dict] = None,
        request_body: Optional[dict] = None,
    ):
        request_info = request_info or {}
        self.protocol = request_info.get("protocol", "")
        self.protocol_version = request_info.get("protocol_version", "")
        self.method = request_info.get("method", "")
        self.path = request_info.get("path", "")
        self.query_params = request_info.get("query_params", {})
        self.host = request_headers.get("host", "")

        self.headers = request_headers or {}
        self.header_params = request_header_params

        request_body = request_body or {}
        self.body = HttpRequestBody(**request_body)
        self.files = self.body.files

        self.context = {}

    def set_context_key(self, key: str, value):
        self.context[key] = value
        return self

    def update_context(self, update: dict):
        self.context.update(update)
        return self

    def set_context(self, context: dict):
        self.context = context
        return self

    def get_context(self):
        return self.context

    def get_headers(self):
        return self.headers


class HttpResponse:
    def __init__(self):
        self.headers = CONSTANTS.get_default_headers()
        self.body = b""
        self.http_version = "HTTP/1.1"
        self.status_code = CONSTANTS.HttpStatusCodes.C_200
        self.DEFAULT_ENCODING = "utf-8"

    def set_http_version(self, version: str):
        self.http_version = (
            f"HTTP/{version}" if not version.startswith("HTTP") else version
        )

        return self

    def set_status_code(self, code: int | str):
        if isinstance(code, str):
            self.status_code = f"{code}"

        else:
            self.status_code = f"{code} {CONSTANTS.get_http_status_code_message(code)}"

        return self

    def set_header(self, header: str, value: str):
        self.headers[header] = value

        return self

    def set_headers(self, headers: dict[str, str]):
        self.headers.update(headers)

        return self

    def set_json(self, data: dict | list):
        self.set_header(
            CONSTANTS.HttpHeaders.CONTENT_TYPE,
            CONSTANTS.HttpContentTypes.APPLICATION_JSON,
        )
        self.body = bytes(JSON.dumps(data), self.DEFAULT_ENCODING)

        return self

    def set_body(self, body: bytes | str):
        self.body = (
            body if isinstance(body, bytes) else bytes(body, self.DEFAULT_ENCODING)
        )

        return self

    def set_html(self, html: str):
        self.set_body(html)
        self.set_header(
            CONSTANTS.HttpHeaders.CONTENT_TYPE, CONSTANTS.HttpContentTypes.TEXT_HTML
        )

        return self

    def set_file(self, filename: str, data: bytes, as_attachment: bool = True):
        self.set_body(data)
        self.set_header(
            CONSTANTS.HttpHeaders.CONTENT_DISPOSITION,
            f"{'attachment' if as_attachment else 'inline'} filename={filename}",
        )
        self.set_header(
            CONSTANTS.HttpHeaders.CONTENT_TYPE,
            f"{get_content_type_from_filename(filename)}",
        )

        return self

    def set_text(self, text: str):
        self.set_body(text)
        self.set_header(
            CONSTANTS.HttpHeaders.CONTENT_TYPE, CONSTANTS.HttpContentTypes.TEXT_PLAIN
        )

        return self

    def build_client_supported_compressions(
        self,
        request_headers: dict = None,
    ):
        accepted_compressions = request_headers.get(
            CONSTANTS.HttpHeaders.ACCEPT_ENCODING, ""
        )

        # Disabling compression : SEEMS TO NOT WORK FOR NON GET REQUESTS
        # accepted_compressions = None

        if accepted_compressions:
            if "gzip" in accepted_compressions:
                self.set_header(CONSTANTS.HttpHeaders.CONTENT_ENCODING, "gzip")
                return gzip.compress(self.body)

            elif "deflate" in accepted_compressions:
                self.set_header(CONSTANTS.HttpHeaders.CONTENT_ENCODING, "deflate")
                return zlib.compress(self.body)

            elif "br" in accepted_compressions:
                self.set_header(CONSTANTS.HttpHeaders.CONTENT_ENCODING, "br")
                return brotli.compress(self.body)

        return self.body

    def build_headers(self):
        items = [f"{self.http_version} {self.status_code}"]
        for key, value in self.headers.items():
            items.append(f"{key}: {value}")

        return bytes("\r\n".join(items), self.DEFAULT_ENCODING)

    def build(self, request_headers: dict = None):
        body = (
            self.build_client_supported_compressions(request_headers=request_headers)
            if request_headers
            else self.body
        )

        result = b""
        self.set_header(CONSTANTS.HttpHeaders.CONTENT_LENGTH, str(len(self.body)))
        result = result + self.build_headers()
        result = result + b"\r\n\r\n"
        result = result + body

        return result
