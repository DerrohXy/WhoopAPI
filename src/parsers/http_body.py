import gzip
import json
import re
import zlib
from email.parser import BytesParser
from email.policy import HTTP

import brotli

import src.constants as CONSTANTS


def parse_multipart_with_regex(boundary: str, body: bytes, charset: str = "utf-8"):
    """
    Parse multipart/form-data using regular expressions only.
    Note: This is less reliable than the email library version.
    Args:
        boundary: The multipart boundary string
        body: The raw request body bytes
        charset: Character encoding for text fields
    Returns:
        Dictionary with form fields and file data
    """
    # Convert boundary to bytes and prepare pattern
    boundary_bytes = boundary.encode("ascii")
    pattern = re.compile(
        b"--"
        + re.escape(boundary_bytes)
        + b"\r\n"
        + b"((?:.|\r\n)*?)\r\n\r\n"  # Headers
        + b"((?:.|\r\n)*?)"  # Content
        + b"(?=\r\n--"
        + re.escape(boundary_bytes)
        + b"(?:--)?\r\n)",
        re.DOTALL,
    )

    form_data = {}
    files = {}

    for match in pattern.finditer(body):
        headers_part, content = match.groups()

        # Parse headers
        headers = {}
        for header_line in headers_part.split(b"\r\n"):
            if b":" in header_line:
                name, value = header_line.split(b":", 1)
                headers[name.strip().lower()] = value.strip()

        # Get field name
        content_disposition = headers.get(b"content-disposition", b"")
        name_match = re.search(rb'name="([^"]+)"', content_disposition)
        if not name_match:
            continue

        name = name_match.group(1).decode("ascii")

        # Check for filename
        filename_match = re.search(rb'filename="([^"]+)"', content_disposition)
        if filename_match:
            # File upload
            files[name] = {
                "filename": filename_match.group(1).decode("ascii"),
                "content_type": headers.get(
                    b"content-type", b"application/octet-stream"
                ).decode("ascii"),
                "data": content,
                "size": len(content),
            }
        else:
            # Regular form field
            try:
                form_data[name] = content.decode(charset)
            except UnicodeDecodeError:
                form_data[name] = content

    return form_data, files


def parse_multipart_enhanced(
    content_type: str, boundary: str, body: bytes
) -> tuple[dict, dict]:
    """
    Parse multipart/form-data body into a dictionary of form fields.
    Uses email library
    Args:
        content_type: The Content-Type header value
        boundary: The boundary value from content type
        body: The raw request body bytes
    Returns:
        Dictionary with field names as keys and field values (str for text, bytes for files)
    """
    combined_content_type = f"{content_type}; boundary={boundary}"
    headers = {"Content-Type": combined_content_type, "Content-Length": str(len(body))}
    msg = BytesParser(policy=HTTP).parsebytes(
        b"\r\n".join([f"{k}: {v}".encode("ascii") for k, v in headers.items()])
        + b"\r\n\r\n"
        + body
    )

    form_data = {}
    files = {}

    for part in msg.iter_parts():
        disposition = part.get("Content-Disposition", "")
        name_match = re.search(r'name="([^"]+)"', disposition)
        if not name_match:
            continue

        name = name_match.group(1)
        filename_match = re.search(r'filename="([^"]+)"', disposition)
        payload = part.get_payload(decode=True)

        if filename_match:
            # Handle file upload
            file_info = {
                "filename": filename_match.group(1),
                "content_type": part.get_content_type(),
                "data": payload,
                "size": len(payload),
            }

            # Handle multiple files with same name
            if name in files:
                if isinstance(files[name], list):
                    files[name].append(file_info)
                else:
                    files[name] = [files[name], file_info]
            else:
                files[name] = file_info
        else:
            # Handle regular form field
            try:
                form_data[name] = payload.decode("utf-8")
            except UnicodeDecodeError:
                form_data[name] = payload

    return form_data, files


def parse_json(content_type: str, data: bytes):
    return json.loads(data)


def handle_compression(headers: dict, body: bytes) -> tuple[dict, bytes]:
    """
    Detects compression and decompresses HTTP request body.
    Returns tuple of (modified_headers, decompressed_body).

    Args:
        headers: Dictionary of HTTP request headers (case-insensitive keys)
        body: Raw request body as bytes

    Returns:
        Tuple of (headers with removed content-encoding, decompressed body)
    """
    decompressed_body = body

    if "content-encoding" in headers:
        encodings = [e.strip().lower() for e in headers["content-encoding"].split(",")]

        # Apply decompressions in reverse order (as per RFC 7231)
        for encoding in reversed(encodings):
            try:
                if encoding == "gzip" or encoding == "x-gzip":
                    decompressed_body = gzip.decompress(decompressed_body)

                elif encoding == "deflate":
                    try:
                        decompressed_body = zlib.decompress(decompressed_body)
                    except zlib.error:
                        # Some servers send raw deflate without zlib header
                        decompressed_body = zlib.decompress(
                            decompressed_body, -zlib.MAX_WBITS
                        )

                elif encoding == "br":
                    decompressed_body = brotli.decompress(decompressed_body)

                elif encoding == "compress" or encoding == "x-compress":
                    raise NotImplementedError("compress encoding not supported")

            except Exception as e:
                raise ValueError(f"Decompression failed for {encoding}: {str(e)}")

        # Remove content-encoding header
        new_headers = headers.copy()
        del new_headers["content-encoding"]
        return new_headers, decompressed_body

    if len(body) >= 2:
        try:
            # Check for gzip magic number (1f 8b)
            if body[:2] == b"\x1f\x8b":
                decompressed_body = gzip.decompress(body)
                return headers, decompressed_body

            # Check for zlib header (78 01, 78 9C, 78 DA)
            elif body[0] == 0x78 and body[1] in {0x01, 0x9C, 0xDA}:
                decompressed_body = zlib.decompress(body)
                return headers, decompressed_body

            # Check for brotli (starts with CE 2F or 1E)
            elif len(body) > 3 and body[0] in {0xCE, 0x1E} and body[1] == 0x2F:
                decompressed_body = brotli.decompress(body)
                return headers, decompressed_body

        except Exception as e:
            raise ValueError(
                f"Auto-detected compression but decompression failed: {str(e)}"
            )

    return headers, body


def parse_body(headers: dict, header_params: dict, data: bytes):
    headers, data = handle_compression(headers=headers, body=data)

    content_type = headers.get(
        CONSTANTS.HttpHeaders.CONTENT_TYPE, CONSTANTS.HttpContentTypes.TEXT_PLAIN
    )
    json_data = None
    form_data = None
    files = None
    text = None

    if content_type in [
        CONSTANTS.HttpContentTypes.TEXT_PLAIN,
        CONSTANTS.HttpContentTypes.TEXT_HTML,
    ]:
        text = data.decode(encoding="utf8")

    if content_type == CONSTANTS.HttpContentTypes.APPLICATION_JSON:
        json_data = parse_json(content_type=content_type, data=data)

    elif content_type == CONSTANTS.HttpContentTypes.MULTIPART_FORM_DATA:
        boundary = header_params.get(CONSTANTS.HttpHeaders.CONTENT_TYPE, {}).get(
            "boundary", ""
        )
        if not boundary:
            raise Exception("Invalid multipart boundary.")

        form_data, files = parse_multipart_enhanced(
            content_type=content_type, boundary=boundary, body=data
        )

    return {
        "json": json_data,
        "form_data": form_data,
        "files": files,
        "text": text,
        "raw": data,
    }
