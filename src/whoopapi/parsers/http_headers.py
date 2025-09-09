import re
from urllib.parse import parse_qs, urlparse


def strip_string(string: str):
    return string.strip()


# def parse_header_line_(header_line):
#     """
#     Parses an HTTP header line with multiple components.
#     Handles headers like:
#     Content-Type: text/html; charset=utf-8
#     Cache-Control: no-cache, no-store, must-revalidate
#     """
#
#     pattern = r"""
#         ^(:?[^:\s]+)              # Header name (group 1) - can start with colon for pseudo-headers
#         \s*:\s*                   # Colon with optional whitespace
#         ([^\x00]*)                # Value (group 2) - no NUL characters allowed
#         ((?:\s*[;,]\s*[^\x00;,]+)*)?  # Additional parameters (group 3, optional)
#         \s*$                      # Trailing whitespace
#     """
#
#     match = re.fullmatch(pattern, header_line, re.VERBOSE)
#     if not match:
#         return None
#
#     header_name = match.group(1).strip().lower()
#     primary_value = match.group(2).strip()
#
#     is_pseudo = header_name.startswith(":")
#     params = {} if not is_pseudo else None
#
#     if not is_pseudo and match.group(3):
#         param_pairs = re.split(r"\s*[;,]\s*", match.group(3).strip())
#         for pair in param_pairs:
#             if "=" in pair:
#                 key, value = pair.split("=", 1)
#                 params[key.strip().lower()] = (
#                     value.strip()
#                 )  # Param names also lowercase
#             elif pair:
#                 params[pair.lower()] = True
#
#     return {
#         "name": header_name,
#         "value": primary_value,
#         "params": params,
#         "is_pseudo": is_pseudo,
#     }


def parse_header_line(header_line):
    """
    Parses an HTTP header line with multiple components.
    Handles headers like:
    Content-Type: text/html; charset=utf-8
    Cache-Control: no-cache, no-store, must-revalidate
    """

    pattern = r"""
        ^(:?[^:\s]+)              # Header name (group 1) - can start with colon for pseudo-headers
        \s*:\s*                   # Colon with optional whitespace
        ([^\x00;,]*)              # Primary value (group 2) - stops at ; or ,
        \s*                       # Optional whitespace
        (?:                       # Non-capturing group for parameters
            [;,]\s*              # Parameter separator (; or ,) with optional whitespace
            ([^\x00]*)           # All parameters (group 3)
        )?
        \s*$                      # Trailing whitespace
    """

    match = re.fullmatch(pattern, header_line, re.VERBOSE)
    if not match:
        return None

    header_name = match.group(1).strip().lower()
    primary_value = match.group(2).strip()
    params_string = match.group(3).strip() if match.group(3) else ""

    is_pseudo = header_name.startswith(":")
    params = {} if not is_pseudo else None

    # Parse parameters
    if not is_pseudo and params_string:
        # Split on semicolons or commas, but be careful with quoted values
        param_pairs = re.split(r"\s*[;,]\s*", params_string)
        for pair in param_pairs:
            if not pair:
                continue
            if "=" in pair:
                key, value = pair.split("=", 1)
                # Remove quotes if present
                value = value.strip()
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                params[key.strip().lower()] = value
            elif pair:
                params[pair.lower()] = True

    return {
        "name": header_name,
        "value": primary_value,
        "params": params,
        "is_pseudo": is_pseudo,
    }


def parse_headers(data: bytes):
    ENCODING = "utf-8"
    HEADER_BREAK = "\r\n"
    stringified = str(data, ENCODING)
    entries = stringified.split(HEADER_BREAK)
    start_line = entries[0].strip()
    split_start_line = start_line.split(" ")
    request_info = {}

    if len(split_start_line) > 2:
        request_info["method"] = strip_string(split_start_line[0])

        request_path = strip_string(split_start_line[1])
        parsed_path = urlparse(url=request_path)
        request_info["path"] = parsed_path.path

        query_params = parse_qs(parsed_path.query)
        request_info["query_params"] = {
            k: v[0] if len(v) == 1 else v for k, v in query_params.items()
        }

        split_version_info = strip_string(split_start_line[2]).split("/")
        request_info["protocol"] = strip_string(strip_string(split_version_info[0]))
        request_info["protocol_version"] = strip_string(split_version_info[1])

    else:
        raise Exception("Invalid headers.")

    entries = entries[1:]
    headers = {}
    header_params = {}

    for entry in entries:
        parsed_line = parse_header_line(header_line=entry)
        if not parsed_line:
            continue

        key = parsed_line["name"]
        value = parsed_line["value"]
        details = parsed_line["params"]
        header_params[key] = details

        headers[key] = value

    return {
        "request_info": request_info,
        "headers": headers,
        "header_params": header_params,
    }
