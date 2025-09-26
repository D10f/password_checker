import socket
import ssl
import sys
import time
from urllib.parse import urlparse

from Headers import Headers
from HttpDate import HttpDate
from Request import Request
from Response import Response

DEFAULT_PORT = 80
DEFAULT_SCHEME = "http"
DEFAULT_HEADERS = {
    "Connection": "keep-alive",
    "User-Agent": "HTTPClient/1.1",
    "Accept-Encoding": "gzip",
    # "Add-Padding": "false",
}
BUFFER_SIZE = 4096
DEFAULT_RETRY_AFTER_TIMEOUT = 600


class HTTPClient:
    def __init__(self, host: str, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.socket = self._create_socket()
        self._default_headers = Headers(DEFAULT_HEADERS)


    def set_headers(self, headers: dict | Headers) -> None:
        if isinstance(headers, Headers):
            self._default_headers.update(headers)
        else:
            self._default_headers.update(headers)


    def set_timeout(self, timeout: float) -> None:
        self.socket.settimeout(timeout)


    def is_connected(self) -> bool:
        if not self.socket:
            return False
        try:
            # Try a zero-byte non-blocking send to check if the socket is connected
            self.socket.getpeername()
            return True
        except socket.error:
            return False


    def close(self) -> None:
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_WR)
                self.socket.close()
            except socket.error:
                pass
            finally:
                self.socket = None


    def get(self, path: str, headers: dict | Headers = None, **kwargs) -> Response:
        response = self._initiate_request("GET", path, headers, **kwargs)

        if response.status_code == 301:
            return self._handle_redirect(response)

        if response.status_code == 429:
            return self._handle_retry_after(response)
            # return self.get("/", headers, **kwargs)

        return response


    def head(self, path: str, headers: dict | Headers = None, **kwargs) -> Response:
        return self._initiate_request("HEAD", path, headers, **kwargs)


    def post(self, path: str, headers: dict | Headers = None, body: bytes = None, **kwargs) -> Response:
        return self._initiate_request("POST", path, headers, body, **kwargs)


    def _initiate_request(
        self,
        method: str,
        path: str,
        headers: dict | Headers = None,
        body: bytes = None,
        **kwargs
    ) -> Response:
        request_headers = Headers(self._default_headers)
        request_headers.update(headers or {})
        request_headers.set("Host", self.host)
        request = Request(method, path, request_headers, body, **kwargs)
        return self._send(request)


    def _handle_retry_after( self, response: Response, timeout: int = DEFAULT_RETRY_AFTER_TIMEOUT ):
        retry_after = response.headers.get("Retry-After")
        req: Request = response.request

        if req.max_retries <= 0:
            raise RuntimeError("Maximum retries exceeded")

        if not retry_after:
            time_to_sleep = req.backoff_factor
        else:
            http_date = HttpDate(retry_after)

            if not http_date.is_future:
                raise RuntimeError("Retry-After header is in the past.")

            print("Retry-After: ", http_date.date)
            time_to_sleep = http_date.diff_in_seconds

        if time_to_sleep > timeout:
            raise RuntimeError("Retry-After/Backoff period is too great.")

        print("Redirecting after", time_to_sleep, "seconds.")
        time.sleep(time_to_sleep)
        return self.get( req.path, headers=req.headers, timeout=req.timeout, max_retries=req.max_retries - 1)


    def _handle_redirect(self, response: Response):

        req: Request = response.request
        location = response.headers.get("Location")
        retry_after = response.headers.has("Retry-After")

        if req.max_redirects <= 0:
            raise RuntimeError("Maximum redirects exceeded")

        if not location:
            raise RuntimeError("Redirect response missing Location header")

        # Handle HTTPS upgrade
        # TODO: Check if location provided is URI or a relative ref (https://www.rfc-editor.org/rfc/rfc3986#section-4.2)
        redirect_url = urlparse(location)
        if redirect_url.scheme == "https" and self.port == 80:
            try:
                self._handle_tls_upgrade()
            except:
                print("Failed to upgrade to HTTPS")

        if retry_after:
            req.path = location
            return self._handle_retry_after(response)

        return self.get(
            location,
            headers=req.headers,
            timeout=req.timeout,
            max_redirects=req.max_redirects - 1,
        )


    def _handle_tls_upgrade(self):
        # Close current connection
        self.close()

        # Creat new socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        # Wrap socket in TLS context
        ctx = ssl.create_default_context()
        # ctx.check_hostname = False
        # ctx.verify_mode = ssl.CERT_NONE
        self.socket = ctx.wrap_socket(sock, server_hostname=self.host)

        # Update destination port
        self.port = 443

        # Establish a new connection
        self.socket.connect((self.host, self.port))


    def _send(self, req: Request) -> Response:
        response_buffer = b""
        response_headers = Headers()
        status_line = ""
        is_chunked_transfer = False

        self.socket.sendall(req.content)

        try:
            while True:
                chunk = self.socket.recv(BUFFER_SIZE)

                if not chunk:
                    break

                response_buffer += chunk

                if b"\r\n\r\n" in response_buffer and response_headers.is_empty():
                    headers_buffer, response_buffer = response_buffer.split(
                        b"\r\n\r\n", 1
                    )
                    status_line, headers_buffer = headers_buffer.decode().split(
                        "\r\n", 1
                    )

                    for header in headers_buffer.split("\r\n"):
                        key, val = header.split(": ", 1)
                        response_headers.set(key, val)

                    # Ignore body for HEAD requests
                    if req.method == "HEAD":
                        response_buffer = b""
                        break

                    is_chunked_transfer = (
                        response_headers.has("Transfer-Encoding")
                        and response_headers.get("Transfer-Encoding") == "chunked"
                    )

                if response_headers.get("Content-Length", ""):
                    bytes_received = len(response_buffer)
                    if bytes_received >= int(response_headers.get("Content-Length")):
                        break
                elif is_chunked_transfer and b"\r\n0\r\n\r\n" in response_buffer:
                    break

        except TimeoutError:
            pass

        return Response(status_line, response_headers, response_buffer, request=req)

    def _create_socket(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.connect((self.host, self.port))
        return sock

    def __enter__(self, host: str = None, port: int = None) -> "HTTPClient":
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        if self.socket is None or self.socket.fileno() == -1:
            self.socket = self._create_socket()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
