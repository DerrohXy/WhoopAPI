WEBSOCKET_ACCEPT_SUFFIX = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
WEBSOCKET_FRAME_MASK = b"abcd"
DEFAULT_STRING_ENCODING = "utf-8"


class HttpHeaders:
    ACCEPT = "accept"
    ACCEPT_CH = "accept-ch"
    ACCEPT_CHARSET = "accept-charset"
    ACCEPT_ENCODING = "accept-encoding"
    ACCEPT_LANGUAGE = "accept-language"
    ACCEPT_PATCH = "accept-patch"
    ACCEPT_POST = "accept-post"
    ACCEPT_RANGES = "accept-ranges"
    ACCESS_CONTROL_ALLOW_CREDENTIALS = "access-control-allow-credentials"
    ACCESS_CONTROL_ALLOW_HEADERS = "access-control-allow-headers"
    ACCESS_CONTROL_ALLOW_METHODS = "access-control-allow-methods"
    ACCESS_CONTROL_ALLOW_ORIGIN = "access-control-allow-origin"
    ACCESS_CONTROL_EXPOSE_HEADERS = "access-control-expose-headers"
    ACCESS_CONTROL_MAX_AGE = "access-control-max-age"
    ACCESS_CONTROL_REQUEST_HEADERS = "access-control-request-headers"
    ACCESS_CONTROL_REQUEST_METHOD = "access-control-request-method"
    AGE = "age"
    ALLOW = "allow"
    ALT_SVC = "alt-svc"
    ALT_USED = "alt-used"
    ATTRIBUTION_REPORTING_ELIGIBLE = "attribution-reporting-eligible"
    ATTRIBUTION_REPORTING_REGISTER_SOURCE = "attribution-reporting-register-source"
    ATTRIBUTION_REPORTING_REGISTER_TRIGGER = "attribution-reporting-register-trigger"
    AUTHORIZATION = "authorization"
    CACHE_CONTROL = "cache-control"
    CLEAR_SITE_DATA = "clear-site-data"
    CONNECTION = "connection"
    CONTENT_DIGEST = "content-digest"
    CONTENT_DISPOSITION = "content-disposition"
    CONTENT_DPR = "content-dpr"
    CONTENT_ENCODING = "content-encoding"
    CONTENT_LANGUAGE = "content-language"
    CONTENT_LENGTH = "content-length"
    CONTENT_LOCATION = "content-location"
    CONTENT_RANGE = "content-range"
    CONTENT_SECURITY_POLICY = "content-security-policy"
    CONTENT_SECURITY_POLICY_REPORT_ONLY = "content-security-policy-report-only"
    CONTENT_TYPE = "content-type"
    COOKIE = "cookie"
    CRITICAL_CH = "critical-ch"
    CROSS_ORIGIN_EMBEDDER_POLICY = "cross-origin-embedder-policy"
    CROSS_ORIGIN_OPENER_POLICY = "cross-origin-opener-policy"
    CROSS_ORIGIN_RESOURCE_POLICY = "cross-origin-resource-policy"
    DATE = "date"
    DEVICE_MEMORY = "device-memory"
    DIGEST = "digest"
    DNT = "dnt"
    DOWNLINK = "downlink"
    DPR = "dpr"
    EARLY_DATA = "early-data"
    ECT = "ect"
    ETAG = "etag"
    EXPECT = "expect"
    EXPECT_CT = "expect-ct"
    EXPIRES = "expires"
    FORWARDED = "forwarded"
    FROM = "from"
    HOST = "host"
    IF_MATCH = "if-match"
    IF_MODIFIED_SINCE = "if-modified-since"
    IF_NONE_MATCH = "if-none-match"
    IF_RANGE = "if-range"
    IF_UNMODIFIED_SINCE = "if-unmodified-since"
    KEEP_ALIVE = "keep-alive"
    LAST_MODIFIED = "last-modified"
    LINK = "link"
    LOCATION = "location"
    MAX_FORWARDS = "max-forwards"
    NEL = "nel"
    NO_VARY_SEARCH = "no-vary-search"
    OBSERVE_BROWSING_TOPICS = "observe-browsing-topics"
    ORIGIN = "origin"
    ORIGIN_AGENT_CLUSTER = "origin-agent-cluster"
    PERMISSIONS_POLICY = "permissions-policy"
    PRAGMA = "pragma"
    PRIORITY = "priority"
    PROXY_AUTHENTICATE = "proxy-authenticate"
    PROXY_AUTHORIZATION = "proxy-authorization"
    RANGE = "range"
    REFERER = "referer"
    REFERRER_POLICY = "referrer-policy"
    REPORTING_ENDPOINTS = "reporting-endpoints"
    REPR_DIGEST = "repr-digest"
    RETRY_AFTER = "retry-after"
    RTT = "rtt"
    SAVE_DATA = "save-data"
    SEC_BROWSING_TOPICS = "sec-browsing-topics"
    SEC_CH_PREFERS_COLOR_SCHEME = "sec-ch-prefers-color-scheme"
    SEC_CH_PREFERS_REDUCED_MOTION = "sec-ch-prefers-reduced-motion"
    SEC_CH_PREFERS_REDUCED_TRANSPARENCY = "sec-ch-prefers-reduced-transparency"
    SEC_CH_UA = "sec-ch-ua"
    SEC_CH_UA_ARCH = "sec-ch-ua-arch"
    SEC_CH_UA_BITNESS = "sec-ch-ua-bitness"
    SEC_CH_UA_FULL_VERSION = "sec-ch-ua-full-version"
    SEC_CH_UA_FULL_VERSION_LIST = "sec-ch-ua-full-version-list"
    SEC_CH_UA_MOBILE = "sec-ch-ua-mobile"
    SEC_CH_UA_MODEL = "sec-ch-ua-model"
    SEC_CH_UA_PLATFORM = "sec-ch-ua-platform"
    SEC_CH_UA_PLATFORM_VERSION = "sec-ch-ua-platform-version"
    SEC_FETCH_DEST = "sec-fetch-dest"
    SEC_FETCH_MODE = "sec-fetch-mode"
    SEC_FETCH_SITE = "sec-fetch-site"
    SEC_FETCH_USER = "sec-fetch-user"
    SEC_GPC = "sec-gpc"
    SEC_PURPOSE = "sec-purpose"
    SEC_WEBSOCKET_ACCEPT = "sec-websocket-accept"
    SEC_WEBSOCKET_KEY = "sec-websocket-key"
    SEC_WEBSOCKET_VERSION = "sec-websocket-version"
    SERVER = "server"
    SERVER_TIMING = "server-timing"
    SERVICE_WORKER_NAVIGATION_PRELOAD = "service-worker-navigation-preload"
    SET_COOKIE = "set-cookie"
    SET_LOGIN = "set-login"
    SOURCEMAP = "sourcemap"
    SPECULATION_RULES = "speculation-rules"
    STRICT_TRANSPORT_SECURITY = "strict-transport-security"
    SUPPORTS_LOADING_MODE = "supports-loading-mode"
    TE = "te"
    TIMING_ALLOW_ORIGIN = "timing-allow-origin"
    TK = "tk"
    TRAILER = "trailer"
    TRANSFER_ENCODING = "transfer-encoding"
    UPGRADE = "upgrade"
    UPGRADE_INSECURE_REQUESTS = "upgrade-insecure-requests"
    USER_AGENT = "user-agent"
    VARY = "vary"
    VIA = "via"
    VIEWPORT_WIDTH = "viewport-width"
    WANT_CONTENT_DIGEST = "want-content-digest"
    WANT_DIGEST = "want-digest"
    WANT_REPR_DIGEST = "want-repr-digest"
    WARNING = "warning"
    WIDTH = "width"
    WWW_AUTHENTICATE = "www-authenticate"
    X_CONTENT_TYPE_OPTIONS = "x-content-type-options"
    X_DNS_PREFETCH_CONTROL = "x-dns-prefetch-control"
    X_FORWARDED_FOR = "x-forwarded-for"
    X_FORWARDED_HOST = "x-forwarded-host"
    X_FORWARDED_PROTO = "x-forwarded-proto"
    X_FRAME_OPTIONS = "x-frame-options"
    X_XSS_PROTECTION = "x-xss-protection"


class HttpMethods:
    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"


class HttpContentTypes:
    APPLICATION_OCTET_STREAM = "application/octet-stream"
    APPLICATION_JSON = "application/json"
    MULTIPART_FORM_DATA = "multipart/form-data"
    TEXT_HTML = "text/html"
    TEXT_PLAIN = "text/plain"


class WebProtocols:
    HTTP = "http"
    WS = "ws"
    HTTPS = "https"
    WSS = "wss"


class HttpStatusCodes_:
    def __init__(self):
        self.C_100 = "100 Continue"
        self.C_101 = "101 Switching Protocols"
        self.C_102 = "102 Processing"
        self.C_200 = "200 OK"
        self.C_201 = "201 Created"
        self.C_202 = "202 Accepted"
        self.C_203 = "203 Non-Authoritative Information"
        self.C_204 = "204 No Content"
        self.C_205 = "205 Reset Content"
        self.C_206 = "206 Partial Content"
        self.C_207 = "207 Multi-Status"
        self.C_208 = "208 Already Reported"
        self.C_226 = "226 IM Used"
        self.C_300 = "300 Multiple Choices"
        self.C_301 = "301 Moved Permanently"
        self.C_302 = "302 Found"
        self.C_303 = "303 See Other"
        self.C_304 = "304 Not Modified"
        self.C_305 = "305 Use Proxy"
        self.C_306 = "306 Reserved"
        self.C_307 = "307 Temporary Redirect"
        self.C_308 = "308 Permanent Redirect"
        self.C_400 = "400 Bad Request"
        self.C_401 = "401 Unauthorized"
        self.C_402 = "402 Payment Required"
        self.C_403 = "403 Forbidden"
        self.C_404 = "404 Not Found"
        self.C_405 = "405 Method Not Allowed"
        self.C_406 = "406 Not Acceptable"
        self.C_407 = "407 Proxy Authentication Required"
        self.C_408 = "408 Request Timeout"
        self.C_409 = "409 Conflict"
        self.C_410 = "410 Gone"
        self.C_411 = "411 Length Required"
        self.C_412 = "412 Precondition Failed"
        self.C_413 = "413 Request Entity Too Large"
        self.C_414 = "414 Request-URI Too Long"
        self.C_415 = "415 Unsupported Media Type"
        self.C_416 = "416 Requested Range Not Satisfiable"
        self.C_417 = "417 Expectation Failed"
        self.C_422 = "422 Unprocessable Entity"
        self.C_423 = "423 Locked"
        self.C_424 = "424 Failed Dependency"
        self.C_426 = "426 Upgrade Required"
        self.C_428 = "428 Precondition Required"
        self.C_429 = "429 Too Many Requests"
        self.C_431 = "431 Request Header Fields Too Large"
        self.C_500 = "500 Internal Server Error"
        self.C_501 = "501 Not Implemented"
        self.C_502 = "502 Bad Gateway"
        self.C_503 = "503 Service Unavailable"
        self.C_504 = "504 Gateway Timeout"
        self.C_505 = "505 HTTP Version Not Supported"
        self.C_506 = "506 Variant Also Negotiates (Experimental)"
        self.C_507 = "507 Insufficient Storage"
        self.C_508 = "508 Loop Detected"
        self.C_510 = "510 Not Extended"
        self.C_511 = "511 Network Authentication Required"


HttpStatusCodes = HttpStatusCodes_()


def get_http_status_code_message(code: int):
    for item in HttpStatusCodes.__dict__.values():
        if isinstance(item, str) and item.startswith(f"{code} "):
            return item[item.index(" ") + 1]

    return "Unknown"


def get_default_headers():
    return {"Server": "WhoopAPI"}


def get_content_type_from_filename(filename: str):
    extension = filename.split(".")[-1] if "." in filename else None
    content_type = None

    if extension:
        content_type = {
            "aac": "audio/aac",
            "abw": "application/x-abiword",
            "arc": "application/octet-stream",
            "avi": "video/x-msvideo",
            "azw": "application/vnd.amazon.ebook",
            "bin": "application/octet-stream",
            "bz": "application/x-bzip",
            "bz2": "application/x-bzip2",
            "csh": "application/x-csh",
            "css": "text/css",
            "csv": "text/csv",
            "doc": "application/msword",
            "epub": "application/epub+zip",
            "gif": "image/gif",
            "htm": "text/html",
            "html": "text/html",
            "ico": "image/x-icon",
            "ics": "text/calendar",
            "jar": "application/java-archive",
            "jpeg": "image.jpeg",
            "jpg": "image/jpeg",
            "js": "application/javascript",
            "json": "application/json",
            "mid": "audio/midi",
            "midi": "audio/midi",
            "mpeg": "video/mpeg",
            "mpkg": "application/vnd.apple.installer+xml",
            "odp": "application/vnd.oasis.opendocument.presentation",
            "ods": "application/vnd.oasis.opendocument.spreadsheet",
            "odt": "application/vnd.oasis.opendocument.text",
            "oga": "audio/ogg",
            "ogv": "video/ogg",
            "ogx": "application/ogg",
            "pdf": "application/pdf",
            "ppt": "application/vnd.ms-powerpoint",
            "rar": "application/x-rar-compressed",
            "rtf": "application/rtf",
            "sh": "application/x-sh",
            "svg": "image/svg+xml",
            "swf": "application/x-shockwave-flash",
            "tar": "application/x-tar",
            "tif": "image/tiff",
            "tiff": "image/tiff",
            "ttf": "font/ttf",
            "vsd": "application/vnd.visio",
            "wav": "audio/x-wav",
            "weba": "audio/webm",
            "webm": "video/webm",
            "webp": "image/webp",
            "woff": "font/woff",
            "woff2": "font/woff2",
            "xhtml": "application/xhtml+xml",
            "xls": "application/vnd.ms-excel",
            "xml": "application/xml",
            "xul": "application/vnd.mozilla.xul+xml",
            "zip": "application/zip",
            "3gp": "video/3gpp",
            # "audio/3gpp if it doesn't contain video": "",
            "3g2": "video/3gpp2",
            # "audio/3gpp2 if it doesn't contain video": "",
            "7z": "application/x-7z-compressed",
        }.get(extension, None)

    return content_type if content_type else HttpContentTypes.APPLICATION_OCTET_STREAM
