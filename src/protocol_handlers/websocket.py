import base64 as BASE64
import hashlib as HASHLIB
import socket as SOCKET
import struct as STRUCT
from typing import Callable

import src.constants as CONSTANTS
from src.logging import LOG_INFO
from src.wrappers import HttpRequest, HttpResponse


def mask_data(mask: bytes, data: bytes):
    masked_data = b""

    for index in range(0, len(data)):
        x = data[index]
        y = mask[index % 4]
        masked_data = masked_data + STRUCT.pack("B", x ^ y)

    return masked_data


def send_websocket_message(socket: SOCKET.socket, message: bytes | str):
    frame_size = 64
    # mask=RANDOM.randbytes(4)
    payloads = []
    index = 0

    while True:
        end = index + frame_size
        if end >= len(message):
            end = len(message)
            payloads.append(message[index:end])

            break

        else:
            payloads.append(message[index:end])

        index = end

    frames = []
    for payload_index in range(0, len(payloads)):
        payload = payloads[payload_index]
        if isinstance(payload, str):
            payload = bytes(payload, CONSTANTS.DEFAULT_STRING_ENCODING)
        # payload=mask_data(mask,payload)
        fin_bit = 0x8000 if payload_index >= len(payloads) - 1 else 0x0000
        rsv_bits = 0x0000

        if payload_index == 0:
            opcode_bits = 0x0200 if isinstance(message, bytes) else 0x0100

        else:
            opcode_bits = 0x0000
        # opcode_bits=0x0200 if payload_index==0 else 0x0000
        # mask_bit=0x0080

        mask_bit = 0x0000
        header = fin_bit | rsv_bits | opcode_bits | mask_bit | len(payload)
        frame = STRUCT.pack(">H", header)
        # frame=frame+mask+payload
        frame = frame + payload
        frames.append(frame)

    for frame in frames:
        socket.sendall(frame)


def read_websocket_message(socket: SOCKET.socket):
    buffer = b""

    while True:
        header = socket.recv(2)
        if header and len(header) == 2:
            header = STRUCT.unpack(">H", header)[0]
            fin = header >> 15
            # opcode = (header << 4) >> 16
            # rsv = (header << 1) >> 13
            mask = (header << 8) >> 15
            payload_length = (header << 9) >> 9
            data_mask = None
            frame_data = None

            if mask > 0:
                data_mask = socket.recv(4)
                if not data_mask:
                    pass

            if payload_length > 0:
                frame_data = socket.recv(payload_length)
                if frame_data:
                    if mask and data_mask:
                        decoded_frame_data = mask_data(data_mask, frame_data)
                        buffer = buffer + decoded_frame_data

                    else:
                        buffer = buffer + frame_data

                else:
                    pass

            if fin > 0:
                break

        else:
            pass

    return buffer


class WebsocketHandler:
    def __init__(self):
        self.route = ""
        self.DEFAULT_ENCODING = "utf-8"
        self.socket = None
        self.running = False

    def set_socket(self, socket: SOCKET.socket):
        self.socket = socket

    def close(self):
        try:
            self.socket.close()
            self.on_close()

        except Exception as e:
            LOG_INFO(e)

    def run(self, timeout=None):
        if not self.socket:
            raise Exception("Socket not set.")

        while True:
            try:
                message = read_websocket_message(self.socket)
                if message:
                    self.on_message(message)

            except Exception as e:
                self.on_error(e)
                self.close()

    def send(self, message: str | bytes):
        try:
            send_websocket_message(self.socket, message)

        except Exception as e:
            self.on_error(e)
            self.close()

    def on_connect(self, request: HttpRequest):
        pass

    def on_message(self, message: bytes):
        pass

    def on_close(self):
        pass

    def on_error(self, exception):
        pass


def path_matches_route(path: str, route: str):
    route_ = route.strip("/ ")
    path_ = path.strip("/ ")
    return path_.startswith(route_)


def handle_websocket_client_request(
    socket: SOCKET.socket,
    request: HttpRequest,
    middlewares: list[Callable],
    websocket_routes: list[tuple[str, Callable | WebsocketHandler]],
):
    request_path = request.path
    handler_found = False

    for action in middlewares:
        action(request)

    for route, handler_function in websocket_routes:
        if isinstance(handler_function, WebsocketHandler):
            handler = handler_function

        else:
            handler = handler_function()

        if path_matches_route(path=request_path, route=route):
            handler_found = True
            handler.route = route
            handler.set_socket(socket)
            handler.on_connect(request)
            handler.run(timeout=1000)

    if not handler_found:
        socket.close()


def generate_websocket_accept_key(websocket_key: str):
    accept_key = f"{websocket_key}{CONSTANTS.WEBSOCKET_ACCEPT_SUFFIX}"
    accept_key = HASHLIB.sha1(accept_key.encode()).digest()
    accept_key = BASE64.b64encode(accept_key).decode("utf-8")

    return accept_key


def perform_websocket_handshake(socket: SOCKET.socket, headers: dict):
    websocket_key = headers.get(CONSTANTS.HttpHeaders.SEC_WEBSOCKET_KEY, "")
    # websocket_version = headers.get(CONSTANTS.HttpHeaders.SEC_WEBSOCKET_VERSION, 13)

    if websocket_key:
        accept_key = generate_websocket_accept_key(websocket_key)
        response = HttpResponse()
        response.set_header(CONSTANTS.HttpHeaders.CONNECTION, "Upgrade")
        response.set_header(CONSTANTS.HttpHeaders.UPGRADE, "websocket")
        response.set_header(CONSTANTS.HttpHeaders.SEC_WEBSOCKET_ACCEPT, accept_key)
        response.set_status_code(CONSTANTS.HttpStatusCodes.C_101)
        result = response.build()
        socket.sendall(result)

        return True

    else:
        return False
