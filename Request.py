from Headers import Headers
from urllib.parse import urlparse, urljoin
import socket


class Request:
    def __init__(self, method: str, path: str, headers: dict | Headers = None, body: str = None, **kwargs):
        self.method = method.upper()
        self.path = Request.validate_path(path)
        self.headers = Headers(headers if Headers else {})
        self.body = body if method in ["POST", "PATCH", "PUT"] else None
        self.timeout = kwargs.get("timeout")
        

    @staticmethod
    def validate_path(path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path

        # Validate path can form valid URL
        test_url = urljoin('https://example.com', path)
        if not urlparse(test_url).path == path:
            raise ValueError(f"Invalid path format: {path}")
        
        return path


    def send(self, s: socket.socket) -> None:
        content = f"{self.method} {self.path} HTTP/1.1\r\n"
        content += str(self.headers) + "\r\n\r\n"

        if self.body:
            content += self.body

        if self.timeout:
            current_timeout = s.gettimeout()
            s.settimeout(self.timeout)

        s.sendall(content.encode())
