import gzip
import json
import unittest
import zlib

import brotli

from src.parsers.http_body import (
    handle_compression,
    parse_body,
    parse_multipart_enhanced,
    parse_multipart_with_regex,
)
from src.parsers.http_headers import parse_header_line, parse_headers


class TestHeadersParser(unittest.TestCase):
    def setUp(self):
        pass

    def test_case1(self):
        sample_header_formats = [
            # Simple key-value
            "Key: value",
            "Key: value123",
            "Key: value-with-hyphen",
            "Key: value_with_underscore",
            "Key: value.with.dots",
            # Multiple values (comma-separated)
            "Key: value1, value2, value3",
            "Key: value1,value2,value3",
            "Key: value1, value2; param=val",
            # Semicolon-delimited parameters
            "Key: value; param=value",
            "Key: value; param1=value1; param2=value2",
            "Key: value; param=123",
            "Key: value; param=true",
            "Key: value; param=false",
            # Quoted values
            'Key: "quoted value"',
            'Key: value; param="quoted value"',
            'Key: "quoted,value"',
            'Key: "quoted;value"',
            # Complex combinations
            "Key: value1, value2; param1=val1, value3; param2=val2",
            'Key: value; param1=val1; param2="quoted,value"',
            "Key: val1; p1=v1, val2; p2=v2; p3=v3",
            # Special characters
            "Key: value!@#$%^&*()",
            "Key: value; param=!@#$%^&*()",
            "Key: value; param=unicode-✓",
            # Whitespace variations
            "Key:   value   ",
            "Key:value",
            "Key:value;param=value",
            "Key  :  value  ;  param  =  value  ",
            # HTTP/2 pseudo-headers
            ":method: GET",
            ":path: /index.html",
            ":authority: example.com",
            # Security headers
            "Strict-Transport-Security: max-age=31536000; includeSubDomains",
            "Content-Security-Policy: default-src 'self'",
            # Authentication headers
            "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
            'WWW-Authenticate: Basic realm="Access to staging site"',
            # Cookie headers
            "Cookie: name=value; name2=value2",
            "Set-Cookie: id=a3fWa; Expires=Wed, 21 Oct 2025 07:28:00 GMT",
            # Cache headers
            "Cache-Control: no-cache, no-store, must-revalidate",
            'ETag: "737060cd8c284d8af7ad3082f209582d"',
            # CORS headers
            "Access-Control-Allow-Origin: *",
            "Access-Control-Allow-Methods: GET, POST, OPTIONS",
            # Non-ASCII
            "X-UTF8-Header: 测试",  # Chinese
            "X-Cyrillic: Тест",  # Russian
            # Non common
            "Key:",
            "Key: ",
            "Key:;",
            "Key: value;",
            "Key: value,;",
        ]

        for format_ in sample_header_formats:
            parsed_item = parse_header_line(header_line=format_)

            self.assertIsNotNone(parsed_item)

    def test_case2(self):
        example_header_data = (
            "GET /api/users?id=123&name=John%20Doe HTTP/1.1\r\n"
            "Host: example.com\r\n"
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n"
            "Accept-Language: en-US,en;q=0.5\r\n"
            "Accept-Encoding: gzip, deflate, br\r\n"
            "Connection: keep-alive\r\n"
            "Cache-Control: max-age=0\r\n"
        )
        example_header_data = example_header_data.encode("utf-8")

        parse_headers(data=example_header_data)


class TestBodyParser(unittest.TestCase):
    def setUp(self):
        pass

    def test_case1(self):
        boundary = "----WebKitFormBoundaryXYZ789"
        content_type = "multipart/form-data"

        title = "Project Files"
        description = "Some nonsense description here"

        example_multipart_body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="title"\r\n'
            "\r\n"
            f"{title}\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="description"\r\n'
            "\r\n"
            f"{description}\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="attachments"; filename="file1.txt"\r\n'
            "Content-Type: text/plain\r\n"
            "\r\n"
            "Contents of file 1\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="attachments"; filename="file2.txt"\r\n'
            "Content-Type: text/plain\r\n"
            "\r\n"
            "Contents of file 2\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")

        form_data, files = parse_multipart_enhanced(
            content_type, boundary, example_multipart_body
        )

        parsed_title = form_data.get("title", None)
        self.assertIsNotNone(parsed_title)
        self.assertEqual(parsed_title, title)

        parsed_description = form_data.get("description", None)
        self.assertIsNotNone(parsed_description)
        self.assertEqual(parsed_description, description)

        attached_files = files.get("attachments", [])
        self.assertEqual(len(attached_files), 2)
        file_names = [t["filename"] for t in attached_files]
        self.assertTrue("file1.txt" in file_names)
        self.assertTrue("file2.txt" in file_names)

        form_data, files = parse_multipart_with_regex(boundary, example_multipart_body)
        parsed_title = form_data.get("title", None)
        self.assertIsNotNone(parsed_title)
        self.assertEqual(parsed_title, title)

        parsed_description = form_data.get("description", None)
        self.assertIsNotNone(parsed_description)
        self.assertEqual(parsed_description, description)

        attached_files = files.get("attachments", {})
        self.assertEqual(attached_files.get("filename"), "file2.txt")

        compressed_body = gzip.compress(b'{"example": "compressed data"}')
        headers = {
            "content-type": "application/json",
            "content-encoding": "gzip",
            "content-length": str(len(compressed_body)),
        }

        new_headers, decompressed_body = handle_compression(headers, compressed_body)

        self.assertFalse("content-encoding" in new_headers)
        decompressed_body = json.loads(decompressed_body)
        self.assertEqual(decompressed_body.get("example", ""), "compressed data")

    def test_case2(self):
        example_json_body = json.dumps(
            {
                "Key1": "Value1",
                "Key2": "Value2",
                "Key3": "Value3",
                "Key4": "Value4",
                "Key5": "Value5",
            }
        ).encode("utf8")
        example_json_headers = {
            "content-type": "application/json",
            "content-length": str(len(example_json_body)),
        }

        parsed_body = parse_body(
            headers=example_json_headers, header_params={}, data=example_json_body
        )
        self.assertIsNotNone(parsed_body.get("json"))
        self.assertIsNone(parsed_body.get("form_data"))
        self.assertIsNone(parsed_body.get("files"))
        parsed_json = parsed_body.get("json")
        self.assertEqual(parsed_json.get("Key1"), "Value1")
        self.assertEqual(parsed_json.get("Key2"), "Value2")

        example_json_body_compressed = gzip.compress(example_json_body)
        example_json_headers_compressed = {
            "content-type": "application/json",
            "content-encoding": "gzip",
            "content-length": str(len(example_json_body_compressed)),
        }

        parsed_body = parse_body(
            headers=example_json_headers_compressed,
            header_params={},
            data=example_json_body_compressed,
        )
        self.assertIsNotNone(parsed_body.get("json"))
        self.assertIsNone(parsed_body.get("form_data"))
        self.assertIsNone(parsed_body.get("files"))
        parsed_json = parsed_body.get("json")
        self.assertEqual(parsed_json.get("Key1"), "Value1")
        self.assertEqual(parsed_json.get("Key2"), "Value2")

        example_json_body_compressed = zlib.compress(example_json_body)
        example_json_headers_compressed = {
            "content-type": "application/json",
            "content-encoding": "deflate",
            "content-length": str(len(example_json_body_compressed)),
        }

        parsed_body = parse_body(
            headers=example_json_headers_compressed,
            header_params={},
            data=example_json_body_compressed,
        )
        self.assertIsNotNone(parsed_body.get("json"))
        self.assertIsNone(parsed_body.get("form_data"))
        self.assertIsNone(parsed_body.get("files"))
        parsed_json = parsed_body.get("json")
        self.assertEqual(parsed_json.get("Key1"), "Value1")
        self.assertEqual(parsed_json.get("Key2"), "Value2")

        example_json_body_compressed = brotli.compress(example_json_body)
        example_json_headers_compressed = {
            "content-type": "application/json",
            "content-encoding": "br",
            "content-length": str(len(example_json_body_compressed)),
        }

        parsed_body = parse_body(
            headers=example_json_headers_compressed,
            header_params={},
            data=example_json_body_compressed,
        )
        self.assertIsNotNone(parsed_body.get("json"))
        self.assertIsNone(parsed_body.get("form_data"))
        self.assertIsNone(parsed_body.get("files"))
        parsed_json = parsed_body.get("json")
        self.assertEqual(parsed_json.get("Key1"), "Value1")
        self.assertEqual(parsed_json.get("Key2"), "Value2")

    def test_case3(self):
        html_text = """
        <html>
            <body>
                <span>Some text here</span>
            </body>
        </html>
        """
        example_html_body = html_text.encode("utf-8")
        example_html_headers = {
            "content-type": "text/html",
            "content-length": str(len(example_html_body)),
        }
        parsed_body = parse_body(
            headers=example_html_headers, header_params={}, data=example_html_body
        )
        self.assertIsNotNone(parsed_body.get("text"))
        self.assertIsNone(parsed_body.get("json"))
        self.assertIsNone(parsed_body.get("form_data"))
        self.assertIsNone(parsed_body.get("files"))
        parsed_text = parsed_body.get("text")
        self.assertEqual(parsed_text, html_text)

        example_html_body_compressed = gzip.compress(example_html_body)
        example_html_headers_compressed = {
            "content-type": "text/html",
            "content-encoding": "gzip",
            "content-length": str(len(example_html_body)),
        }
        parsed_body = parse_body(
            headers=example_html_headers_compressed,
            header_params={},
            data=example_html_body_compressed,
        )
        self.assertIsNotNone(parsed_body.get("text"))
        self.assertIsNone(parsed_body.get("json"))
        self.assertIsNone(parsed_body.get("form_data"))
        self.assertIsNone(parsed_body.get("files"))
        parsed_text = parsed_body.get("text")
        self.assertEqual(parsed_text, html_text)

    def test_case4(self):
        boundary = "----WebKitFormBoundaryXYZ789"
        content_type = "multipart/form-data"

        title = "Project Files"
        description = "Some nonsense description here"

        example_multipart_body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="title"\r\n'
            "\r\n"
            f"{title}\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="description"\r\n'
            "\r\n"
            f"{description}\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="attachments"; filename="file1.txt"\r\n'
            "Content-Type: text/plain\r\n"
            "\r\n"
            "Contents of file 1\r\n"
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="attachments"; filename="file2.txt"\r\n'
            "Content-Type: text/plain\r\n"
            "\r\n"
            "Contents of file 2\r\n"
            f"--{boundary}--\r\n"
        ).encode("utf-8")
        example_multipart_headers = {
            "content-type": content_type,
            "content-length": str(len(example_multipart_body)),
        }
        parsed_body = parse_body(
            headers=example_multipart_headers,
            header_params={"content-type": {"boundary": boundary}},
            data=example_multipart_body,
        )
        self.assertIsNotNone(parsed_body.get("form_data"))
        self.assertIsNotNone(parsed_body.get("files"))
        self.assertIsNone(parsed_body.get("text"))
        self.assertIsNone(parsed_body.get("json"))
        parsed_form = parsed_body.get("form_data")
        self.assertEqual(parsed_form.get("title"), title)
        self.assertEqual(parsed_form.get("description"), description)
        parsed_files = parsed_body.get("files")
        attachments = parsed_files.get("attachments")
        self.assertTrue(len(attachments), 2)

        example_multipart_body_compressed = gzip.compress(example_multipart_body)
        example_multipart_headers_compressed = {
            "content-type": content_type,
            "content-encoding": "gzip",
            "content-length": str(len(example_multipart_body_compressed)),
        }
        parsed_body = parse_body(
            headers=example_multipart_headers_compressed,
            header_params={"content-type": {"boundary": boundary}},
            data=example_multipart_body_compressed,
        )
        self.assertIsNotNone(parsed_body.get("form_data"))
        self.assertIsNotNone(parsed_body.get("files"))
        self.assertIsNone(parsed_body.get("text"))
        self.assertIsNone(parsed_body.get("json"))
        parsed_form = parsed_body.get("form_data")
        self.assertEqual(parsed_form.get("title"), title)
        self.assertEqual(parsed_form.get("description"), description)
        parsed_files = parsed_body.get("files")
        attachments = parsed_files.get("attachments")
        self.assertTrue(len(attachments), 2)
