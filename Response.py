import Headers


class Response:

    def __init__(self, status_line: str, headers: Headers, body: bytes):
        _, status_line = status_line.split(' ', 1)
        status_code, status_reason = status_line.split(' ', 1)
        self.status_code = int(status_code)
        self.status_reason = status_reason.strip()
        self.headers = headers
        self.body = body

    def __str__(self):
        return f"{self.status_code} {self.status_reason}"

    @property
    def text(self):
        return self.body.decode()

    @property
    def json(self):
        import json
        return json.loads(self.body)
