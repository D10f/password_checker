import Headers
import Request


class Response:

    def __init__(self, status_line: str, headers: Headers, body: bytes, request: Request = None):
        http_version, status_code, status_reason = status_line.split(' ', 2)
        self.http_version = http_version
        self.status_code = int(status_code)
        self.status_reason = status_reason.strip()
        self.headers = headers
        self._body = body
        self.request = request

    def __str__(self):
        return f"{self.status_code} {self.status_reason}"

    @property
    def raw(self):
        return self._body

    @property
    def text(self):
        content_type = self.headers.get("Content-Type")
        charset = "utf-8"

        if "charset" in content_type:
            _, charset_type = content_type.split("charset=", 1)
            charset_type = charset_type.strip(";")
            # charset_type = charset_type.strip(";", 1)[0]

            if charset_type.startswith("'") or charset_type.startswith('"'):
                charset = charset_type[1:-1]
            else:
                charset = charset_type

        try:
            return self._get_body().decode(charset)
        except UnicodeDecodeError as e:
            raise e

    @property
    def json(self):
        import json
        try:
            body = self._get_body()
            return json.loads(body)
        except json.JSONDecodeError as e:
            raise e


    def _get_body(self):
        encoding = self.headers.get("Content-Encoding")

        if not encoding:
            return self._body

        if encoding == "gzip":
            import gzip

            try:
                gzip_begin = self._body.find(b'\x1f\x8b') # Gzip magic numbers
                gzip_end = len(b'\r\n0\r\n\r\n')    # RFC 7230 chunk
                return gzip.decompress(self._body[gzip_begin:-gzip_end])
            except gzip.BadGzipFile as e:
                raise e

        raise RuntimeError("Response encoded in unsupported encoding: " + encoding)
