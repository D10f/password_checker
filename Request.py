import re
from Headers import Headers

UNRESERVED = r"[a-zA-Z0-9-._~]"
PCT_ENC    = r"%[a-fA-F0-9]{2}"
SUB_DELIMS = r"[!$&'()*+,;=]"
PCHAR      = rf"({UNRESERVED}|{PCT_ENC}|{SUB_DELIMS}|:|@)"

URL_MATCHER = re.compile(rf"""^
    # Path component
    (
        (/({{PCHAR}}+(/{{PCHAR}}*)*)?)
        | (/{{PCHAR}}*)*
        | ({{PCHAR}}+(/{{PCHAR}}*)*)
        | ({{PCHAR}}{0})
    )
    
    # Query component
    (\?({{PCHAR}}|\/|\?)*)?
    
    # Fragment component
    (\#({{PCHAR}}|\/|\?)*)?
""".replace("{{PCHAR}}", PCHAR), re.VERBOSE)

def validate_path_or_throw(path: str):
    if not URL_MATCHER.match(path):
        raise ValueError(f"Invalid path format: {path}")
    return path

class Request:
    def __init__(self, method: str, path: str, headers: dict | Headers = None, body: str | bytes = None, timeout: float = None, max_redirects: int = 5, max_retries: int = 5, backoff_factor: float = 0.2):
        self.method = method.upper()
        self.headers = Headers(headers if Headers else {})
        self.path = validate_path_or_throw(path)
        self.body = body if method in ["POST", "PATCH", "PUT"] else None
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    @property
    def content(self):
        content = f"{self.method} {self.path} HTTP/1.1\r\n"
        content += str(self.headers) + "\r\n\r\n"

        if self.body:
            if isinstance(self.body, str):
                content += self.body
            else:
                content += self.body.decode()

        return content.encode()

    @property
    def backoff_timeout(self):
        return self.backoff_factor * (2 ** (self.max_retries - 1))